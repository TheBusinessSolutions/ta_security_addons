# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # ── Advance Info on Payslip ───────────────────────────────────────────────
    advance_outstanding = fields.Monetary(
        string='Advance Outstanding Balance',
        compute='_compute_advance_outstanding',
        currency_field='advance_currency_id',
        help='Total outstanding advance balance for this employee at time of payslip.',
    )
    # Use a dedicated currency field to avoid conflict with community payroll
    # which may or may not define currency_id on hr.payslip
    advance_currency_id = fields.Many2one(
        'res.currency',
        compute='_compute_advance_currency_id',
        string='Currency (Advance)',
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

    def _compute_advance_currency_id(self):
        """Get the company currency safely regardless of payroll version."""
        for slip in self:
            slip.advance_currency_id = slip.company_id.currency_id if slip.company_id else self.env.company.currency_id

    def _compute_advance_outstanding(self):
        """Show the employee's total outstanding advance balance."""
        LedgerLine = self.env['hr.advance.ledger.line']
        for slip in self:
            if slip.employee_id:
                slip.advance_outstanding = LedgerLine.get_employee_balance(
                    slip.employee_id.id
                )
            else:
                slip.advance_outstanding = 0.0

    # ─────────────────────────────────────────────────────────────────────────
    # Override action_payslip_done to handle SAR → ledger entry
    # ─────────────────────────────────────────────────────────────────────────

    def action_payslip_done(self):
        """
        On payslip confirmation:
        1. Call super() — community payroll just sets state='done'
        2. Look for SAR input line (code = 'SAR') on the payslip
        3. If SAR amount > 0:
           a. Validate against employee outstanding balance
           b. Create a CR ledger line — reduces the employee advance balance
           c. No GL entry here: the SAR salary rule in the payroll structure
              handles the accounting (DR Salary Expense / CR Advance Account)
        """
        res = super().action_payslip_done()

        for slip in self:
            # Community payroll state after done is 'done'
            if slip.state != 'done':
                continue

            sar_amount = self._get_sar_amount(slip)
            if not sar_amount or sar_amount <= 0:
                continue

            # Validate employee has outstanding balance
            LedgerLine = self.env['hr.advance.ledger.line']
            employee_balance = LedgerLine.get_employee_balance(slip.employee_id.id)

            if employee_balance <= 0:
                raise UserError(_(
                    'Employee %s has no outstanding advance balance, '
                    'but a SAR deduction of %.2f is set on the payslip.\n'
                    'Please remove the SAR input line or register an advance first.'
                ) % (slip.employee_id.name, sar_amount))

            if sar_amount > employee_balance:
                raise UserError(_(
                    'SAR deduction (%.2f) exceeds employee %s outstanding '
                    'balance (%.2f).\nPlease reduce the SAR amount.'
                ) % (sar_amount, slip.employee_id.name, employee_balance))

            # Create CR ledger line — this is the key: reduces outstanding balance
            self._create_payslip_ledger_line(slip, sar_amount)

        return res

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _get_sar_amount(self, slip):
        """
        Read the SAR input line from the payslip.
        In hr_payroll_community, inputs are hr.payslip.input records
        linked via input_line_ids with a direct 'code' field.
        Returns 0.0 if no SAR line found.
        """
        for line in slip.input_line_ids:
            if line.code == 'SAR':
                return line.amount or 0.0
        return 0.0

    def _get_employee_advance_account(self, employee):
        """
        Get the advance account from the employee's most recent disbursed advance.
        Used by external callers (e.g. reports).
        """
        advance = self.env['hr.salary.advance'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'disbursed'),
        ], order='date desc', limit=1)
        return advance.advance_account_id if advance else False

    def _create_payslip_ledger_line(self, slip, amount):
        """
        Create a Credit ledger line from a payslip SAR deduction.
        This reduces the employee's outstanding advance balance.
        No journal entry is created here — the salary rule handles GL.
        """
        period_str = ''
        if slip.date_from:
            period_str = '%s/%s' % (slip.date_from.month, slip.date_from.year)

        return self.env['hr.advance.ledger.line'].create({
            'employee_id': slip.employee_id.id,
            'date': slip.date_to or fields.Date.today(),
            'line_type': 'credit',
            'amount': amount,
            'description': _('Salary Deduction - %s (%s)') % (
                slip.name or slip.number or _('Payslip'), period_str
            ),
            'source': 'payslip',
            'payslip_id': slip.id,
            # move_id intentionally omitted:
            # hr_payroll_community does not create account.move on payslip confirm
        })
