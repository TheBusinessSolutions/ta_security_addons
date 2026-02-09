from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HrLoanPayment(models.Model):
    _name = 'hr.loan.payment'
    _description = 'Loan Payment'
    _order = 'date desc, id desc'

    loan_id = fields.Many2one(
        'hr.loan',
        required=True,
        ondelete='cascade'
    )

    employee_id = fields.Many2one(
        related='loan_id.employee_id',
        store=True,
        readonly=True
    )

    date = fields.Date(
        default=fields.Date.context_today,
        required=True
    )

    amount = fields.Float(required=True)

    payment_method = fields.Selection([
        ('payroll', 'Payroll'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
    ], required=True)

    payslip_id = fields.Many2one('hr.payslip')
    move_id = fields.Many2one('account.move')

    @api.constrains('amount')
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("Payment amount must be positive.")
