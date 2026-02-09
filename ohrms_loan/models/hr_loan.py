from odoo import api, fields, models


class HrLoan(models.Model):
    _inherit = 'hr.loan'

    payment_ids = fields.One2many(
        'hr.loan.payment',
        'loan_id',
        string='Payments'
    )

    total_paid_amount = fields.Float(
        compute='_compute_payment_amounts',
        store=True
    )

    balance_amount = fields.Float(
        compute='_compute_payment_amounts',
        store=True
    )

    @api.depends('loan_amount', 'payment_ids.amount')
    def _compute_payment_amounts(self):
        for loan in self:
            total_paid = sum(loan.payment_ids.mapped('amount'))
            loan.total_paid_amount = total_paid
            loan.balance_amount = loan.loan_amount - total_paid
