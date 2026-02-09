from odoo import api, fields, models


class HrLoan(models.Model):
    _inherit = 'hr.loan'

    # Link to payment records
    payment_ids = fields.One2many(
        'hr.loan.payment',
        'loan_id',
        string='Payments'
    )

    # Computed total paid and remaining balance
    total_paid_amount = fields.Float(
        compute='_compute_payment_amounts',
        store=True,
        string='Total Paid'
    )

    balance_amount = fields.Float(
        compute='_compute_payment_amounts',
        store=True,
        string='Balance Amount'
    )

    @api.depends('loan_amount', 'payment_ids.amount')
    def _compute_payment_amounts(self):
        """ Compute total paid and remaining balance """
        for loan in self:
            total_paid = sum(loan.payment_ids.mapped('amount'))
            loan.total_paid_amount = total_paid
            loan.balance_amount = loan.loan_amount - total_paid
