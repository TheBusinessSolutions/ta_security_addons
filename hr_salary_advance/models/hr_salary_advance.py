# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrSalaryAdvance(models.Model):
    _name = 'hr.salary.advance'
    _description = 'Employee Salary Advance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    # ─── Identity ────────────────────────────────────────────────────────────
    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        tracking=True,
        states={'draft': [('readonly', False)], 'refused': [('readonly', False)]},
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
    )
    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        related='employee_id.job_id',
        store=True,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        string='Currency',
    )

    # ─── Advance Details ─────────────────────────────────────────────────────
    date = fields.Date(
        string='Request Date',
        required=True,
        default=fields.Date.today,
        tracking=True,
    )
    amount = fields.Monetary(
        string='Advance Amount',
        required=True,
        currency_field='currency_id',
        tracking=True,
    )
    reason = fields.Text(
        string='Reason / Notes',
    )

    # ─── Accounting Configuration ─────────────────────────────────────────────
    advance_account_id = fields.Many2one(
        'account.account',
        string='Advance Account (Asset)',
        required=True,
        domain="[('account_type', 'in', ['asset_current', 'asset_non_current'])]",
        tracking=True,
        help='GL account to debit when advance is disbursed (e.g. 141000 - Salary Advances)',
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Journal',
        required=True,
        domain="[('type', 'in', ['cash', 'bank'])]",
        tracking=True,
        help='Journal used when disbursing the advance (Cash or Bank)',
    )

    # ─── Status & Workflow ────────────────────────────────────────────────────
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Finance Approved'),
        ('disbursed', 'Disbursed'),
        ('refused', 'Refused'),
    ], string='Status', default='draft', tracking=True, copy=False)

    # ─── Computed Balance Fields ──────────────────────────────────────────────
    total_repaid = fields.Monetary(
        string='Total Repaid',
        compute='_compute_repaid_balance',
        store=True,
        currency_field='currency_id',
    )
    outstanding_balance = fields.Monetary(
        string='Outstanding Balance (This Advance)',
        compute='_compute_repaid_balance',
        store=True,
        currency_field='currency_id',
    )

    # ─── Employee-wide Balance (across ALL advances) ──────────────────────────
    employee_total_outstanding = fields.Monetary(
        string='Employee Total Outstanding',
        compute='_compute_employee_outstanding',
        currency_field='currency_id',
    )

    # ─── Move / Approval Info ─────────────────────────────────────────────────
    move_id = fields.Many2one(
        'account.move',
        string='Disbursement Journal Entry',
        readonly=True,
        copy=False,
    )
    approved_by = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        copy=False,
    )
    approved_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
        copy=False,
    )
    disbursed_by = fields.Many2one(
        'res.users',
        string='Disbursed By',
        readonly=True,
        copy=False,
    )
    disbursed_date = fields.Datetime(
        string='Disbursement Date',
        readonly=True,
        copy=False,
    )

    # ─── Ledger Lines ─────────────────────────────────────────────────────────
    ledger_line_ids = fields.One2many(
        'hr.advance.ledger.line',
        'advance_id',
        string='Repayment Lines',
        readonly=True,
    )

    # ─────────────────────────────────────────────────────────────────────────
    # Constraints
    # ─────────────────────────────────────────────────────────────────────────

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_('Advance amount must be positive.'))

    # ─────────────────────────────────────────────────────────────────────────
    # Computed Methods
    # ─────────────────────────────────────────────────────────────────────────

    @api.depends('ledger_line_ids', 'ledger_line_ids.amount', 'ledger_line_ids.line_type', 'amount')
    def _compute_repaid_balance(self):
        for rec in self:
            repaid = sum(
                line.amount for line in rec.ledger_line_ids
                if line.line_type == 'credit'
            )
            rec.total_repaid = repaid
            rec.outstanding_balance = rec.amount - repaid

    def _compute_employee_outstanding(self):
        """Compute total outstanding balance across ALL advances for this employee."""
        for rec in self:
            if not rec.employee_id:
                rec.employee_total_outstanding = 0.0
                continue
            all_advances = self.search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'disbursed'),
                ('id', '!=', rec.id if rec.id else 0),
            ])
            # Sum all disbursed amounts
            total_disbursed = sum(all_advances.mapped('amount'))
            # Sum all repaid amounts from ledger
            total_repaid = sum(
                line.amount
                for adv in all_advances
                for line in adv.ledger_line_ids
                if line.line_type == 'credit'
            )
            # Add current record's outstanding too (if disbursed)
            current_outstanding = rec.outstanding_balance if rec.state == 'disbursed' else 0.0
            rec.employee_total_outstanding = (total_disbursed - total_repaid) + current_outstanding

    # ─────────────────────────────────────────────────────────────────────────
    # ORM Overrides
    # ─────────────────────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.salary.advance') or _('New')
        return super().create(vals_list)

    # ─────────────────────────────────────────────────────────────────────────
    # Workflow Actions
    # ─────────────────────────────────────────────────────────────────────────

    def action_submit(self):
        """Employee/HR submits the advance request."""
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_('Only draft advances can be submitted.'))
            rec.state = 'submitted'
            rec.message_post(body=_('Advance request submitted for Finance approval.'))

    def action_approve(self):
        """Finance Manager approves the advance."""
        self._check_finance_manager()
        for rec in self:
            if rec.state != 'submitted':
                raise UserError(_('Only submitted advances can be approved.'))
            rec.write({
                'state': 'approved',
                'approved_by': self.env.user.id,
                'approved_date': fields.Datetime.now(),
            })
            rec.message_post(body=_('Advance approved by %s.') % self.env.user.name)

    def action_refuse(self):
        """Finance Manager refuses the advance."""
        self._check_finance_manager()
        for rec in self:
            if rec.state not in ('submitted', 'approved'):
                raise UserError(_('Only submitted or approved advances can be refused.'))
            rec.write({'state': 'refused'})
            rec.message_post(body=_('Advance refused by %s.') % self.env.user.name)

    def action_reset_draft(self):
        """Reset refused advance back to draft."""
        for rec in self:
            if rec.state != 'refused':
                raise UserError(_('Only refused advances can be reset to draft.'))
            rec.state = 'draft'

    def action_disburse(self):
        """
        Disburse the advance:
        DR  Advance Account (Asset)   [employee gets the money]
        CR  Payment Journal Account   [cash/bank goes out]
        Then create a DR ledger line for this employee.
        """
        self._check_finance_manager()
        for rec in self:
            if rec.state != 'approved':
                raise UserError(_('Only approved advances can be disbursed.'))
            if not rec.advance_account_id or not rec.journal_id:
                raise UserError(_('Please set the Advance Account and Payment Journal before disbursing.'))

            # Get the payment account from the journal
            payment_account = rec.journal_id.default_account_id
            if not payment_account:
                raise UserError(
                    _('Journal "%s" has no default account configured.') % rec.journal_id.name
                )

            # Build journal entry
            move_vals = {
                'move_type': 'entry',
                'date': fields.Date.today(),
                'ref': _('Salary Advance: %s - %s') % (rec.name, rec.employee_id.name),
                'journal_id': rec.journal_id.id,
                'line_ids': [
                    # DR Advance Account
                    (0, 0, {
                        'name': _('Salary Advance - %s') % rec.employee_id.name,
                        'account_id': rec.advance_account_id.id,
                        'debit': rec.amount,
                        'credit': 0.0,
                        'partner_id': rec.employee_id.address_home_id.id if rec.employee_id.address_home_id else False,
                    }),
                    # CR Cash/Bank
                    (0, 0, {
                        'name': _('Salary Advance Payment - %s') % rec.employee_id.name,
                        'account_id': payment_account.id,
                        'debit': 0.0,
                        'credit': rec.amount,
                        'partner_id': rec.employee_id.address_home_id.id if rec.employee_id.address_home_id else False,
                    }),
                ],
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()

            # Create DR ledger line
            self.env['hr.advance.ledger.line'].create({
                'employee_id': rec.employee_id.id,
                'advance_id': rec.id,
                'date': fields.Date.today(),
                'line_type': 'debit',
                'amount': rec.amount,
                'description': _('Advance Disbursed: %s') % rec.name,
                'move_id': move.id,
            })

            rec.write({
                'state': 'disbursed',
                'move_id': move.id,
                'disbursed_by': self.env.user.id,
                'disbursed_date': fields.Datetime.now(),
            })
            rec.message_post(
                body=_('Advance of %s %s disbursed. Journal Entry: %s') % (
                    rec.amount, rec.currency_id.symbol, move.name
                )
            )

    def action_register_cash_payment(self):
        """Open wizard to register a manual cash/bank repayment."""
        self.ensure_one()
        if self.state != 'disbursed':
            raise UserError(_('Can only register payments for disbursed advances.'))
        if self.outstanding_balance <= 0:
            raise UserError(_('This advance has no outstanding balance.'))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Register Advance Repayment'),
            'res_model': 'hr.advance.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_advance_id': self.id,
                'default_employee_id': self.employee_id.id,
                'default_amount': self.outstanding_balance,
                'default_advance_account_id': self.advance_account_id.id,
            },
        }

    def action_view_ledger(self):
        """Open the employee advance ledger filtered for this employee."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Advance Ledger - %s') % self.employee_id.name,
            'res_model': 'hr.advance.ledger.line',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.employee_id.id)],
            'context': {'default_employee_id': self.employee_id.id},
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Helper Methods
    # ─────────────────────────────────────────────────────────────────────────

    def _check_finance_manager(self):
        """Ensure current user is a Finance Manager."""
        if not self.env.user.has_group('account.group_account_manager'):
            raise UserError(_(
                'Only Finance Managers can perform this action. '
                'Please contact your Finance Manager.'
            ))

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        """Refresh employee outstanding balance when employee changes."""
        if self.employee_id:
            self._compute_employee_outstanding()
