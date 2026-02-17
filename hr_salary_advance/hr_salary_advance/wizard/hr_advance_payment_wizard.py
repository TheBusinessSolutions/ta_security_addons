# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrAdvancePaymentWizard(models.TransientModel):
    """
    Wizard to register a manual cash/bank repayment of a salary advance.

    Flow:
        Employee returns money via cash or bank transfer.
        Finance Manager opens this wizard from the advance form.
        On confirm:
            1. GL Entry:  DR Cash/Bank  |  CR Advance Account
            2. Ledger CR line created for the employee
            3. Advance outstanding_balance reduces accordingly
    """
    _name = 'hr.advance.payment.wizard'
    _description = 'Register Advance Repayment (Cash / Bank)'

    advance_id = fields.Many2one(
        'hr.salary.advance',
        string='Advance',
        required=True,
        readonly=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        related='advance_id.employee_id',
        readonly=True,
    )
    company_id = fields.Many2one(
        'res.company',
        related='advance_id.company_id',
    )
    currency_id = fields.Many2one(
        'res.currency',
        related='advance_id.currency_id',
    )
    outstanding_balance = fields.Monetary(
        string='Outstanding Balance',
        related='advance_id.outstanding_balance',
        currency_field='currency_id',
        readonly=True,
    )

    # ─── Payment Details ──────────────────────────────────────────────────────
    date = fields.Date(
        string='Payment Date',
        required=True,
        default=fields.Date.today,
    )
    amount = fields.Monetary(
        string='Amount to Repay',
        required=True,
        currency_field='currency_id',
    )
    journal_id = fields.Many2one(
        'account.journal',
        string='Payment Journal',
        required=True,
        domain="[('type', 'in', ['cash', 'bank'])]",
        help='Journal where the cash/bank repayment is received.',
    )
    advance_account_id = fields.Many2one(
        'account.account',
        string='Advance Account',
        required=True,
        readonly=True,
        help='The advance asset account to credit (reduces outstanding balance).',
    )
    notes = fields.Text(
        string='Notes / Reference',
    )

    # ─────────────────────────────────────────────────────────────────────────
    # Constraints
    # ─────────────────────────────────────────────────────────────────────────

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_('Payment amount must be positive.'))
            if rec.amount > rec.outstanding_balance:
                raise ValidationError(_(
                    'Payment amount (%s) cannot exceed outstanding balance (%s).'
                ) % (rec.amount, rec.outstanding_balance))

    # ─────────────────────────────────────────────────────────────────────────
    # Action
    # ─────────────────────────────────────────────────────────────────────────

    def action_confirm_payment(self):
        """
        Post GL entry and create CR ledger line.

        GL Entry:
            DR  Cash/Bank Account       (money coming in)
            CR  Advance Account (Asset) (reduces what employee owes)
        """
        self.ensure_one()
        self._check_finance_manager()

        advance = self.advance_id
        if advance.state != 'disbursed':
            raise UserError(_('Can only register payments for disbursed advances.'))

        if self.amount > advance.outstanding_balance:
            raise UserError(_(
                'Payment amount (%s) exceeds outstanding balance (%s).'
            ) % (self.amount, advance.outstanding_balance))

        # Get the debit (cash/bank) account from the journal
        debit_account = self.journal_id.default_account_id
        if not debit_account:
            raise UserError(
                _('Journal "%s" has no default account configured.') % self.journal_id.name
            )

        # Build journal entry
        partner = advance.employee_id.address_home_id if advance.employee_id.address_home_id else False
        move_vals = {
            'move_type': 'entry',
            'date': self.date,
            'ref': _('Advance Repayment: %s - %s') % (advance.name, advance.employee_id.name),
            'journal_id': self.journal_id.id,
            'line_ids': [
                # DR Cash/Bank (money comes in)
                (0, 0, {
                    'name': _('Advance Repayment (Cash) - %s') % advance.employee_id.name,
                    'account_id': debit_account.id,
                    'debit': self.amount,
                    'credit': 0.0,
                    'partner_id': partner.id if partner else False,
                }),
                # CR Advance Account (reduces asset / what employee owes)
                (0, 0, {
                    'name': _('Advance Repayment - %s [%s]') % (
                        advance.employee_id.name, advance.name
                    ),
                    'account_id': self.advance_account_id.id,
                    'debit': 0.0,
                    'credit': self.amount,
                    'partner_id': partner.id if partner else False,
                }),
            ],
        }

        move = self.env['account.move'].create(move_vals)
        move.action_post()

        # Create CR ledger line
        notes_suffix = ' - %s' % self.notes if self.notes else ''
        self.env['hr.advance.ledger.line'].create({
            'employee_id': advance.employee_id.id,
            'advance_id': advance.id,
            'date': self.date,
            'line_type': 'credit',
            'amount': self.amount,
            'description': _('Cash/Bank Repayment [%s]%s') % (advance.name, notes_suffix),
            'source': 'cash',
            'move_id': move.id,
        })

        # Log on the advance
        advance.message_post(
            body=_('Cash repayment of %s %s registered. Journal Entry: %s') % (
                self.amount, advance.currency_id.symbol, move.name
            )
        )

        return {'type': 'ir.actions.act_window_close'}

    def _check_finance_manager(self):
        """Ensure current user is a Finance Manager."""
        if not self.env.user.has_group('account.group_account_manager'):
            raise UserError(_(
                'Only Finance Managers can register advance repayments.'
            ))
