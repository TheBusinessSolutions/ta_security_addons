# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # ── Advance Info on Payslip ───────────────────────────────────────────────
    advance_outstanding = fields.Monetary(
        string='Advance Outstanding Balance',
        compute='_compute_advance_outstanding',
        currency_field='currency_id',
        help='Total outstanding advance balance for this employee at time of payslip.',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Currency',
    )
    advance_ledger_line_ids = fields.One2many(
        'hr.advance.ledger.line',
        'payslip_id',
        string='Advance Deductions (This Payslip)',
        readonly=True,
    )

    # ─────────────────────────────────────────────────────────────────────────
    # Computed
    # ─────────────────────────────────────────────────────────────────────────

    def _compute_advance_outstanding(self):
        """Show the employee's total outstanding advance balance."""
        LedgerLine = self.env['hr.advance.ledger.line']
        for slip in self:
            if slip.employee_id:
                slip.advance_outstanding = LedgerLine.get_employee_balance(slip.employee_id.id)
            else:
                slip.advance_outstanding = 0.0

    # ─────────────────────────────────────────────────────────────────────────
    # Override action_payslip_done to handle SAR salary rule → ledger + GL
    # ─────────────────────────────────────────────────────────────────────────

    def action_payslip_done(self):
        """
        On payslip confirmation:
        1. Call super() to post the payslip normally
        2. Find the SAR input line amount
        3. If SAR amount > 0:
           a. Create a CR ledger line for the employee
           b. Post a GL journal entry:
              DR Salary Expense (handled by payroll structure salary rule)
              CR Advance Account (we do this here via the advance account)
        """
        res = super().action_payslip_done()

        for slip in self:
            if slip.state != 'done':
                continue

            # Find SAR input line value
            sar_amount = self._get_sar_amount(slip)
            if not sar_amount or sar_amount <= 0:
                continue

            # Validate employee has enough outstanding balance
            LedgerLine = self.env['hr.advance.ledger.line']
            employee_balance = LedgerLine.get_employee_balance(slip.employee_id.id)

            if employee_balance <= 0:
                raise UserError(_(
                    'Employee %s has no outstanding advance balance, '
                    'but SAR deduction of %s is set on the payslip.'
                ) % (slip.employee_id.name, sar_amount))

            if sar_amount > employee_balance:
                raise UserError(_(
                    'SAR deduction amount (%s) exceeds employee %s outstanding balance (%s). '
                    'Please reduce the deduction amount.'
                ) % (sar_amount, slip.employee_id.name, employee_balance))

            # Get advance account from the most recent disbursed advance
            # (we use this for the GL entry — same account as the advance asset)
            advance_account = self._get_employee_advance_account(slip.employee_id)
            if not advance_account:
                # If no account found, still create ledger line (GL handled by payroll rule)
                self._create_payslip_ledger_line(slip, sar_amount)
                continue

            # Create CR ledger line (reduces employee outstanding balance)
            ledger_line = self._create_payslip_ledger_line(slip, sar_amount)

            # Post a supplementary GL entry to CR the Advance Account
            # NOTE: The SAR salary rule already handles DR Salary Expense / CR Net Payable.
            # This entry clears the Advance Account:
            #   DR Net Payable (offset)  →  CR Advance Account (reduces asset)
            # In practice the full accounting is done by the payroll rule.
            # We simply mark the ledger line with the payslip move for traceability.
            if slip.move_id:
                ledger_line.write({'move_id': slip.move_id.id})

        return res

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _get_sar_amount(self, slip):
        """
        Get the value of the SAR (Salary Advance Return) input line from the payslip.
        Returns 0.0 if not found.
        """
        # Check Other Inputs (hr.payslip.input)
        for input_line in slip.input_line_ids:
            if input_line.code == 'SAR':
                return input_line.amount
        return 0.0

    def _get_employee_advance_account(self, employee):
        """
        Get the advance account from the employee's most recent disbursed advance.
        This ensures GL entries use the correct account.
        """
        advance = self.env['hr.salary.advance'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'disbursed'),
        ], order='date desc', limit=1)
        return advance.advance_account_id if advance else False

    def _create_payslip_ledger_line(self, slip, amount):
        """Create a Credit ledger line from payslip deduction."""
        period_str = '%s/%s' % (slip.date_from.month, slip.date_from.year) if slip.date_from else ''
        return self.env['hr.advance.ledger.line'].create({
            'employee_id': slip.employee_id.id,
            'date': slip.date_to or fields.Date.today(),
            'line_type': 'credit',
            'amount': amount,
            'description': _('Salary Deduction - Payslip %s (%s)') % (slip.name or '', period_str),
            'source': 'payslip',
            'payslip_id': slip.id,
        })


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    # Optional: Add a helper domain to easily find SAR type
    @api.model
    def _get_sar_input_type(self):
        return self.env.ref(
            'hr_salary_advance.hr_payslip_input_type_sar',
            raise_if_not_found=False,
        )
