from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class HrLoan(models.Model):
    """ Model for managing loan requests."""
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Loan Request"

    @api.model
    def default_get(self, field_list):
        """ Function used to pass employee corresponding to current login user
            as default employee while creating new loan request"""
        result = super(HrLoan, self).default_get(field_list)
        if result.get('user_id'):
            user_id = result['user_id']
        else:
            user_id = self.env.context.get('user_id', self.env.user.id)
        result['employee_id'] = self.env['hr.employee'].search(
            [('user_id', '=', user_id)], limit=1).id
        return result

    name = fields.Char(
        string="Loan Name", 
        default="New", 
        readonly=True,
        help="Name of the loan", 
        tracking=True
    )
    date = fields.Date(
        string="Date", 
        default=fields.Date.today(),
        readonly=True, 
        help="Date of the loan request"
    )
    employee_id = fields.Many2one(
        'hr.employee', 
        string="Employee",
        required=True, 
        help="Employee Name",
        tracking=True
    )
    department_id = fields.Many2one(
        'hr.department',
        related="employee_id.department_id",
        readonly=True, 
        string="Department",
        help="The department to which the employee belongs.",
        store=True
    )
    installment = fields.Integer(
        string="No Of Installments", 
        default=1,
        help="Number of installments"
    )
    payment_date = fields.Date(
        string="Payment Start Date", 
        required=True,
        default=fields.Date.today(),
        help="Date of the first payment"
    )
    loan_lines = fields.One2many(
        'hr.loan.line', 
        'loan_id',
        string="Loan Installments",
        help="Installment schedule"
    )
    payment_lines = fields.One2many(
        'hr.loan.payment', 
        'loan_id',
        string="Direct Payments",
        help="Direct payments made outside payslip"
    )
    company_id = fields.Many2one(
        'res.company', 
        string='Company',
        help="Company",
        default=lambda self: self.env.user.company_id
    )
    currency_id = fields.Many2one(
        'res.currency', 
        string='Currency',
        required=True, 
        help="Currency",
        default=lambda self: self.env.user.company_id.currency_id
    )
    job_position = fields.Many2one(
        'hr.job',
        related="employee_id.job_id",
        readonly=True, 
        string="Job Position",
        help="Job position of the employee",
        store=True
    )
    loan_amount = fields.Float(
        string="Loan Amount", 
        required=True,
        help="Total loan amount", 
        tracking=True
    )
    total_amount = fields.Float(
        string="Total Amount", 
        store=True,
        readonly=True, 
        compute='_compute_total_amount',
        help="The total amount of the loan"
    )
    balance_amount = fields.Float(
        string="Balance Amount", 
        store=True,
        compute='_compute_total_amount',
        help="Remaining balance to be paid",
        tracking=True
    )
    total_paid_amount = fields.Float(
        string="Total Paid Amount", 
        store=True,
        compute='_compute_total_amount',
        help="Total amount paid (payslip + direct)",
        tracking=True
    )
    payslip_paid_amount = fields.Float(
        string="Paid via Payslip", 
        store=True,
        compute='_compute_total_amount',
        help="Amount paid through payslip deductions"
    )
    direct_paid_amount = fields.Float(
        string="Paid Directly", 
        store=True,
        compute='_compute_total_amount',
        help="Amount paid directly (outside payslip)"
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval_1', 'Submitted'),
        ('approve', 'Approved'),
        ('refuse', 'Refused'),
        ('cancel', 'Canceled'),
        ('closed', 'Fully Paid')
    ], string="State", default='draft', help="Loan status", 
       copy=False, tracking=True)
    
    # Accounting Fields - FIXED DOMAINS
    loan_account_id = fields.Many2one(
        'account.account',
        string="Loan Account",
        required=True,
        domain="[('account_type', '=', 'asset_current'), ('deprecated', '=', False)]",
        help="Employee Loan Receivable Account (Current Asset)"
    )
    treasury_account_id = fields.Many2one(
        'account.account',
        string="Disbursement Account",
        required=True,
        domain="[('account_type', 'in', ['asset_cash', 'asset_current_receivable']), ('deprecated', '=', False)]",
        help="Cash/Bank account used for loan disbursement"
    )
    journal_id = fields.Many2one(
        'account.journal',
        string="Journal",
        required=True,
        domain="[('type', 'in', ['cash', 'bank'])]",
        help="Journal for loan transactions"
    )
    move_id = fields.Many2one(
        'account.move',
        string="Disbursement Entry",
        readonly=True,
        help="Journal entry for loan disbursement",
        copy=False
    )

    @api.depends('loan_lines.paid', 'loan_lines.amount', 
                 'payment_lines.state', 'payment_lines.amount', 
                 'loan_amount')
    def _compute_total_amount(self):
        """ Compute loan amounts based on payslip deductions and direct payments """
        for loan in self:
            # Calculate payslip payments
            payslip_paid = sum(
                line.amount for line in loan.loan_lines if line.paid
            )
            
            # Calculate direct payments
            direct_paid = sum(
                payment.amount for payment in loan.payment_lines 
                if payment.state == 'posted'
            )
            
            total_paid = payslip_paid + direct_paid
            
            loan.total_amount = loan.loan_amount
            loan.payslip_paid_amount = payslip_paid
            loan.direct_paid_amount = direct_paid
            loan.total_paid_amount = total_paid
            loan.balance_amount = loan.loan_amount - total_paid
            
            # Auto-close loan when fully paid
            if loan.state == 'approve' and loan.balance_amount <= 0:
                loan.state = 'closed'

    @api.model
    def create(self, values):
        """ Check pending loans and assign sequence """
        loan_count = self.env['hr.loan'].search_count(
            [('employee_id', '=', values['employee_id']),
             ('state', '=', 'approve'),
             ('balance_amount', '!=', 0)])
        if loan_count:
            raise ValidationError(_(
                "This employee already has a pending loan with outstanding balance."
            ))
        
        values['name'] = self.env['ir.sequence'].next_by_code('hr.loan.seq') or _('New')
        return super(HrLoan, self).create(values)

    def action_compute_installment(self):
        """ Generate installment schedule """
        for loan in self:
            loan.loan_lines.unlink()
            date_start = datetime.strptime(str(loan.payment_date), '%Y-%m-%d')
            amount = loan.loan_amount / loan.installment
            
            for i in range(1, loan.installment + 1):
                self.env['hr.loan.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id
                })
                date_start = date_start + relativedelta(months=1)
        return True

    def action_approve(self):
        """ Approve loan and create disbursement accounting entry """
        for loan in self:
            if not loan.loan_lines:
                raise ValidationError(_("Please compute installments first!"))
            
            if not loan.loan_account_id or not loan.treasury_account_id:
                raise ValidationError(_(
                    "Please configure:\n- Loan Account\n- Disbursement Account\n- Journal"
                ))
            
            # Create disbursement entry
            move_vals = {
                'ref': _('Loan Disbursement - %s') % loan.name,
                'journal_id': loan.journal_id.id,
                'date': loan.date,
                'line_ids': [
                    # Debit: Loan Receivable (Employee owes company)
                    (0, 0, {
                        'name': _('Loan to %s') % loan.employee_id.name,
                        'account_id': loan.loan_account_id.id,
                        'debit': loan.loan_amount,
                        'credit': 0.0,
                        'partner_id': loan.employee_id.address_home_id.id if loan.employee_id.address_home_id else False,
                    }),
                    # Credit: Cash/Bank (Money paid to employee)
                    (0, 0, {
                        'name': _('Loan to %s') % loan.employee_id.name,
                        'account_id': loan.treasury_account_id.id,
                        'debit': 0.0,
                        'credit': loan.loan_amount,
                        'partner_id': loan.employee_id.address_home_id.id if loan.employee_id.address_home_id else False,
                    }),
                ]
            }
            
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            
            loan.write({
                'state': 'approve',
                'move_id': move.id
            })
            
            loan.message_post(
                body=_('Loan approved. Disbursement entry: %s') % move.name
            )
        
        return True

    def action_register_payment(self):
        """ Open wizard to register direct payment """
        self.ensure_one()
        return {
            'name': _('Register Loan Payment'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.loan.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_loan_id': self.id,
                'default_amount': self.balance_amount,
                'default_employee_id': self.employee_id.id,
            }
        }

    def action_refuse(self):
        """ Refuse loan request """
        return self.write({'state': 'refuse'})

    def action_submit(self):
        """ Submit loan for approval """
        self.write({'state': 'waiting_approval_1'})

    def action_cancel(self):
        """ Cancel loan - only if no payments made """
        for loan in self:
            if loan.total_paid_amount > 0:
                raise ValidationError(_(
                    'Cannot cancel! Payments already made: %s %s'
                ) % (loan.currency_id.symbol, '{:,.2f}'.format(loan.total_paid_amount)))
            
            # Reverse disbursement entry
            if loan.move_id and loan.move_id.state == 'posted':
                reversal = loan.move_id._reverse_moves([{
                    'date': fields.Date.today(),
                    'ref': _('Reversal: %s') % loan.move_id.name
                }], cancel=True)
                if reversal:
                    reversal.action_post()
            
            loan.write({'state': 'cancel'})
        return True

    def action_set_to_draft(self):
        """ Reset to draft """
        for loan in self:
            if loan.total_paid_amount > 0:
                raise ValidationError(_('Cannot reset - payments already made'))
            loan.write({'state': 'draft'})
        return True

    def unlink(self):
        """ Prevent deletion of non-draft loans """
        for loan in self:
            if loan.state not in ('draft', 'cancel'):
                raise UserError(_(
                    'Cannot delete a loan that is not in Draft or Cancelled state'
                ))
        return super(HrLoan, self).unlink()


class HrLoanLine(models.Model):
    """ Loan installment schedule """
    _name = "hr.loan.line"
    _description = "Loan Installment"
    _order = "date"

    date = fields.Date(string="Due Date", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee")
    amount = fields.Float(string="Amount", required=True)
    paid = fields.Boolean(string="Paid", default=False)
    loan_id = fields.Many2one('hr.loan', string="Loan", ondelete='cascade')
    payslip_id = fields.Many2one('hr.payslip', string="Payslip", readonly=True)


class HrLoanPayment(models.Model):
    """ Direct loan payments (outside payslip) """
    _name = "hr.loan.payment"
    _description = "Direct Loan Payment"
    _order = "payment_date desc"

    name = fields.Char(
        string="Payment Reference", 
        readonly=True, 
        default="New"
    )
    loan_id = fields.Many2one(
        'hr.loan', 
        string="Loan", 
        required=True, 
        ondelete='cascade'
    )
    employee_id = fields.Many2one(
        'hr.employee', 
        string="Employee", 
        required=True
    )
    payment_date = fields.Date(
        string="Payment Date", 
        required=True, 
        default=fields.Date.today
    )
    amount = fields.Float(
        string="Amount", 
        required=True
    )
    journal_id = fields.Many2one(
        'account.journal', 
        string="Payment Journal", 
        required=True,
        domain="[('type', 'in', ['cash', 'bank'])]"
    )
    payment_account_id = fields.Many2one(
        'account.account', 
        string="Payment Account", 
        required=True,
        domain="[('account_type', 'in', ['asset_cash', 'asset_current_receivable']), ('deprecated', '=', False)]"
    )
    notes = fields.Text(string="Notes")
    move_id = fields.Many2one(
        'account.move', 
        string="Journal Entry", 
        readonly=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')
    ], string="Status", default='draft', readonly=True)
    company_id = fields.Many2one(
        'res.company', 
        default=lambda self: self.env.company
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.loan.payment') or _('New')
        return super(HrLoanPayment, self).create(vals)

    def action_post(self):
        """ Post the direct payment and create accounting entry """
        for payment in self:
            if payment.state == 'posted':
                continue
            
            loan = payment.loan_id
            
            # Create accounting entry
            move_vals = {
                'ref': _('Direct Loan Payment - %s - %s') % (loan.name, payment.name),
                'journal_id': payment.journal_id.id,
                'date': payment.payment_date,
                'line_ids': [
                    # Debit: Cash/Bank (Money received)
                    (0, 0, {
                        'name': _('Loan Payment from %s') % loan.employee_id.name,
                        'account_id': payment.payment_account_id.id,
                        'debit': payment.amount,
                        'credit': 0.0,
                        'partner_id': loan.employee_id.address_home_id.id if loan.employee_id.address_home_id else False,
                    }),
                    # Credit: Loan Receivable (Reduce what employee owes)
                    (0, 0, {
                        'name': _('Loan Payment from %s') % loan.employee_id.name,
                        'account_id': loan.loan_account_id.id,
                        'debit': 0.0,
                        'credit': payment.amount,
                        'partner_id': loan.employee_id.address_home_id.id if loan.employee_id.address_home_id else False,
                    }),
                ]
            }
            
            move = self.env['account.move'].create(move_vals)
            move.action_post()
            
            payment.write({
                'move_id': move.id,
                'state': 'posted'
            })
            
            loan.message_post(
                body=_('Direct payment posted: %s %s (Entry: %s)') % (
                    loan.currency_id.symbol,
                    '{:,.2f}'.format(payment.amount),
                    move.name
                )
            )
        
        return True

    def action_cancel(self):
        """ Cancel payment and reverse entry """
        for payment in self:
            if payment.move_id and payment.move_id.state == 'posted':
                reversal = payment.move_id._reverse_moves([{
                    'date': fields.Date.today(),
                    'ref': _('Reversal: %s') % payment.move_id.name
                }], cancel=True)
                if reversal:
                    reversal.action_post()
            
            payment.write({'state': 'cancel'})
        return True

    def unlink(self):
        """ Prevent deletion of posted payments """
        for payment in self:
            if payment.state == 'posted':
                raise UserError(_('Cannot delete a posted payment. Cancel it first.'))
        return super(HrLoanPayment, self).unlink()


class HrLoanPaymentWizard(models.TransientModel):
    """ Wizard to register direct loan payment """
    _name = "hr.loan.payment.wizard"
    _description = "Register Loan Payment"

    loan_id = fields.Many2one('hr.loan', string="Loan", required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    payment_date = fields.Date(
        string="Payment Date", 
        required=True, 
        default=fields.Date.today
    )
    amount = fields.Float(string="Amount", required=True)
    journal_id = fields.Many2one(
        'account.journal', 
        string="Payment Journal", 
        required=True,
        domain="[('type', 'in', ['cash', 'bank'])]"
    )
    payment_account_id = fields.Many2one(
        'account.account', 
        string="Received In", 
        required=True,
        domain="[('account_type', 'in', ['asset_cash', 'asset_current_receivable']), ('deprecated', '=', False)]"
    )
    notes = fields.Text(string="Notes")

    def action_register_payment(self):
        """ Create and post the payment """
        self.ensure_one()
        
        payment = self.env['hr.loan.payment'].create({
            'loan_id': self.loan_id.id,
            'employee_id': self.employee_id.id,
            'payment_date': self.payment_date,
            'amount': self.amount,
            'journal_id': self.journal_id.id,
            'payment_account_id': self.payment_account_id.id,
            'notes': self.notes,
        })
        
        payment.action_post()
        
        return {'type': 'ir.actions.act_window_close'}