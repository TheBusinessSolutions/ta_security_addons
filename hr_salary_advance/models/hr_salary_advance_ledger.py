# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrAdvanceLedgerLine(models.Model):
    """
    Running DR/CR ledger for employee salary advances.

    Every financial event (disbursement, salary deduction, cash repayment)
    creates a line here, giving a full statement per employee.

    DR lines = money given to employee (advance disbursed)
    CR lines = money recovered from employee (salary deduction or cash return)
    Balance  = total amount still owed by employee
    """
    _name = 'hr.advance.ledger.line'
    _description = 'Employee Advance Ledger Line'
    _order = 'date asc, id asc'

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        index=True,
        ondelete='restrict',
    )
    advance_id = fields.Many2one(
        'hr.salary.advance',
        string='Advance Reference',
        ondelete='restrict',
        index=True,
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
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.today,
    )
    line_type = fields.Selection([
        ('debit', 'Debit (DR) — Advance Given'),
        ('credit', 'Credit (CR) — Amount Recovered'),
    ], string='Type', required=True)

    amount = fields.Monetary(
        string='Amount',
        required=True,
        currency_field='currency_id',
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    source = fields.Selection([
        ('advance', 'Advance Disbursement'),
        ('payslip', 'Salary Deduction'),
        ('cash', 'Cash / Bank Repayment'),
    ], string='Source', required=True, default='advance')

    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
    )
    payslip_id = fields.Many2one(
        'hr.payslip',
        string='Payslip',
        readonly=True,
    )

    # ── Running Balance (computed, stored for performance) ────────────────────
    running_balance = fields.Monetary(
        string='Balance',
        compute='_compute_running_balance',
        store=True,
        currency_field='currency_id',
        help='Running balance of all advance transactions for this employee up to this line.',
    )

    @api.depends(
        'employee_id', 'date', 'id',
        'line_type', 'amount',
    )
    def _compute_running_balance(self):
        """
        Compute running balance for each line in chronological order per employee.
        Uses a Python loop (not SQL window function) for Odoo compatibility.
        """
        # Group lines by employee
        employees = self.mapped('employee_id')
        for employee in employees:
            # Get ALL lines for this employee, ordered by date then id
            all_lines = self.search([
                ('employee_id', '=', employee.id),
            ], order='date asc, id asc')

            running = 0.0
            for line in all_lines:
                if line.line_type == 'debit':
                    running += line.amount
                else:
                    running -= line.amount
                line.running_balance = running

    # ─────────────────────────────────────────────────────────────────────────
    # Class-level Helper (used by other models)
    # ─────────────────────────────────────────────────────────────────────────

    @api.model
    def get_employee_balance(self, employee_id):
        """
        Return the current total outstanding balance for an employee.
        This is the sum of all DR lines minus sum of all CR lines.
        """
        lines = self.search([('employee_id', '=', employee_id)])
        total_dr = sum(l.amount for l in lines if l.line_type == 'debit')
        total_cr = sum(l.amount for l in lines if l.line_type == 'credit')
        return total_dr - total_cr

    @api.model
    def get_employee_statement(self, employee_id, date_from=None, date_to=None):
        """
        Return statement lines for an employee within optional date range.
        """
        domain = [('employee_id', '=', employee_id)]
        if date_from:
            domain.append(('date', '>=', date_from))
        if date_to:
            domain.append(('date', '<=', date_to))
        return self.search(domain, order='date asc, id asc')
