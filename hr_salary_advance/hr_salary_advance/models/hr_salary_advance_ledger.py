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

    # ── Running Balance (computed live — never stored, always accurate) ──────
    running_balance = fields.Monetary(
        string='Balance',
        compute='_compute_running_balance',
        store=False,
        currency_field='currency_id',
        help='Running balance of all advance transactions for this employee up to this line.',
    )

    @api.depends('employee_id', 'date', 'line_type', 'amount')
    def _compute_running_balance(self):
        """
        Compute running balance for each line in chronological order per employee.

        NOTE: We intentionally do NOT store this field.
        A stored running balance would go stale whenever a new line is inserted
        before existing lines (e.g. backdated entry). Computing live is always correct.

        For each employee in the current recordset, we fetch ALL their ledger lines
        ordered by date + id, compute the cumulative balance, then assign back only
        to the lines that belong to self (the current compute batch).
        """
        # Identify which employees appear in the current batch
        employee_ids = self.mapped('employee_id').ids
        if not employee_ids:
            for rec in self:
                rec.running_balance = 0.0
            return

        # For each employee, compute the full running balance across ALL their lines
        # We need all lines (not just self) to get correct cumulative values
        all_lines_by_employee = {}
        for emp_id in employee_ids:
            all_lines = self.search(
                [('employee_id', '=', emp_id)],
                order='date asc, id asc',
            )
            running = 0.0
            balance_map = {}
            for line in all_lines:
                if line.line_type == 'debit':
                    running += line.amount
                else:
                    running -= line.amount
                balance_map[line.id] = running
            all_lines_by_employee[emp_id] = balance_map

        # Assign only to records in self
        for rec in self:
            emp_map = all_lines_by_employee.get(rec.employee_id.id, {})
            rec.running_balance = emp_map.get(rec.id, 0.0)

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
