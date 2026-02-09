from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"

    name = fields.Char(default="New", readonly=True)
    date = fields.Date(default=fields.Date.context_today, readonly=True)

    employee_id = fields.Many2one('hr.employee', required=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company
    )

    currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        readonly=True
    )

    loan_amount = fields.Float(string="Loan Amount", required=True)

    payment_ids = fields.One2many(
        'hr.loan.payment',
        'loan_id',
        string='Payments'
    )

    total_paid_amount = fields.Float(
        compute='_compute_amounts',
        store=True
    )

    balance_amount = fields.Float(
        compute='_compute_amounts',
        store=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Submitted'),
        ('approve', 'Approved'),
        ('cancel', 'Canceled'),
    ], default='draft', tracking=True)

    @api.depends('loan_amount', 'payment_ids.amount')
    def _compute_amounts(self):
        for loan in self:
            total_paid = sum(loan.payment_ids.mapped('amount'))
            loan.total_paid_amount = total_paid
            loan.balance_amount = loan.loan_amount - total_paid

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.loan.seq')
        return super().create(vals)
