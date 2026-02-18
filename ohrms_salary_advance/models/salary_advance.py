# -*- coding: utf-8 -*-
#############################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
import time
from odoo.exceptions import UserError
from odoo import api, fields, models, _


class SalaryAdvance(models.Model):
    """Salary Advance model — supports multiple concurrent open advances per
    employee. The total outstanding approved advances are guarded against a
    maximum ceiling defined as max_percent of the employee contract wage."""

    _name = "salary.advance"
    _description = "Salary Advance"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------
    name = fields.Char(
        string='Name', readonly=True,
        default=lambda self: 'Adv/',
        help='Sequence reference of the salary advance.')
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True,
        help='Employee requesting the advance.')
    date = fields.Date(
        string='Date', required=True,
        default=lambda self: fields.Date.today(),
        help='Date of the advance request.')
    reason = fields.Text(
        string='Reason',
        help='Reason provided by the employee for requesting the advance.')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id,
        help='Currency used for this advance.')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id,
        help='Company of the employee.')
    advance = fields.Float(
        string='Advance Amount', required=True,
        help='Amount being requested as a salary advance.')
    payment_method = fields.Many2one(
        'account.journal', string='Payment Method',
        help='Payment journal used to disburse the advance.')
    exceed_condition = fields.Boolean(
        string='Exceed Maximum',
        help='Check this to allow the advance to exceed the maximum percentage '
             'configured on the salary structure. Requires HR Manager approval.')
    department = fields.Many2one(
        'hr.department', string='Department',
        related='employee_id.department_id',
        help='Department of the employee (auto-filled).')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submit', 'Submitted'),
            ('waiting_approval', 'Waiting Approval'),
            ('approve', 'Approved'),
            ('cancel', 'Cancelled'),
            ('reject', 'Rejected'),
        ],
        string='Status', default='draft',
        tracking=True,
        help='Current state of the salary advance request.')
    debit = fields.Many2one(
        'account.account', string='Debit Account',
        help='Account debited when the advance is disbursed (e.g. Employee '
             'Advance Account).')
    credit = fields.Many2one(
        'account.account', string='Credit Account',
        help='Account credited when the advance is disbursed (e.g. Cash/Bank).')
    journal = fields.Many2one(
        'account.journal', string='Journal',
        help='Accounting journal used to post the advance entry.')
    employee_contract_id = fields.Many2one(
        'hr.contract', string='Contract',
        related='employee_id.contract_id',
        help='Active contract of the employee (auto-filled).')

    # ------------------------------------------------------------------
    # Computed: total outstanding approved advances for this employee.
    # Used in the form view as an informational field so both HR and
    # Accounting can see the current exposure before approving.
    # ------------------------------------------------------------------
    total_outstanding_advance = fields.Float(
        string='Total Outstanding Advances',
        compute='_compute_total_outstanding_advance',
        help='Sum of all approved (not yet fully deducted) advances for this '
             'employee. Used to check against the maximum ceiling.')

    # -------------------------------------------------------------------------
    # Computed methods
    # -------------------------------------------------------------------------
    @api.depends('employee_id', 'state')
    def _compute_total_outstanding_advance(self):
        """Compute the total of all *other* approved advances for the same
        employee so that the form shows real-time exposure."""
        for rec in self:
            if not rec.employee_id:
                rec.total_outstanding_advance = 0.0
                continue
            approved = self.search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', '=', 'approve'),
                ('id', '!=', rec._origin.id),
            ])
            rec.total_outstanding_advance = sum(approved.mapped('advance'))

    # -------------------------------------------------------------------------
    # Onchange
    # -------------------------------------------------------------------------
    @api.onchange('company_id')
    def _onchange_company_id(self):
        """Restrict journal domain to the selected company."""
        company = self.company_id
        return {
            'domain': {
                'journal': [('company_id', '=', company.id)],
            }
        }

    # -------------------------------------------------------------------------
    # Button actions — state transitions
    # -------------------------------------------------------------------------
    def action_submit_to_manager(self):
        """Employee submits the request to their HR manager."""
        self.state = 'submit'

    def action_cancel(self):
        """Cancel a draft or submitted advance."""
        self.state = 'cancel'

    def action_reject(self):
        """HR manager rejects the advance during waiting-approval stage."""
        self.state = 'reject'

    # -------------------------------------------------------------------------
    # ORM overrides
    # -------------------------------------------------------------------------
    @api.model
    def create(self, vals):
        """Assign a sequence number on creation."""
        vals['name'] = (
            self.env['ir.sequence'].get('salary.advance.seq') or '/'
        )
        return super().create(vals)

    # -------------------------------------------------------------------------
    # Approval helpers
    # -------------------------------------------------------------------------
    def _check_advance_ceiling(self):
        """Validate that adding this advance does not exceed the maximum
        outstanding balance allowed by the salary structure.

        Ceiling = (max_percent / 100) * contract wage

        If max_percent is 0 on the structure the check is skipped (no limit
        configured). The `exceed_condition` flag on the record lets an HR
        manager explicitly bypass the ceiling — useful for exceptional cases.
        """
        self.ensure_one()
        if self.exceed_condition:
            # Manager has explicitly allowed exceeding the limit.
            return

        contract = self.employee_contract_id
        if not contract:
            return  # Contract check is handled separately.

        max_percent = contract.struct_id.max_percent if contract.struct_id else 0
        if not max_percent:
            return  # No ceiling configured — allow freely.

        max_allowed = (max_percent / 100.0) * contract.wage

        # Current outstanding advances (already approved, excluding this one)
        existing_approved = self.search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'approve'),
            ('id', '!=', self.id),
        ])
        outstanding = sum(existing_approved.mapped('advance'))

        if outstanding + self.advance > max_allowed:
            raise UserError(
                _(
                    'Cannot approve this advance.\n\n'
                    'Employee: %(name)s\n'
                    'Requested: %(req).2f\n'
                    'Current outstanding advances: %(out).2f\n'
                    'Maximum allowed (%(pct)s%% of %(wage).2f wage): %(max).2f\n\n'
                    'Total would be %(total).2f which exceeds the ceiling of '
                    '%(max).2f.\n\n'
                    'To override, tick the "Exceed Maximum" checkbox before '
                    'resubmitting.'
                ) % {
                    'name': self.employee_id.name,
                    'req': self.advance,
                    'out': outstanding,
                    'pct': max_percent,
                    'wage': contract.wage,
                    'max': max_allowed,
                    'total': outstanding + self.advance,
                }
            )

    def approve_request(self):
        """HR Manager first-level approval.

        Checks performed:
        1. Employee must have a home address.
        2. Employee must have an active contract.
        3. Advance amount must be > 0.
        4. This month's payslip must not already be confirmed.
        5. Aggregate outstanding balance must not exceed the ceiling
           (unless exceed_condition is ticked).

        Removed from original:
        - One-advance-per-month restriction (replaced by ceiling check above).
        - advance_date day restriction (removed per client requirement).
        """
        self.ensure_one()

        if not self.employee_id.address_id:
            raise UserError(
                _('Please define a home address for employee "%s".\n'
                  'Go to the employee form → Private Information tab.')
                % self.employee_id.name
            )

        if not self.employee_contract_id:
            raise UserError(
                _('No active contract found for employee "%s". '
                  'Please define a contract before approving an advance.')
                % self.employee_id.name
            )

        if not self.advance or self.advance <= 0:
            raise UserError(_('Please enter a valid advance amount greater than zero.'))

        # Block if this month's payslip is already confirmed.
        payslip_done = self.env['hr.payslip'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'done'),
            ('date_from', '<=', self.date),
            ('date_to', '>=', self.date),
        ], limit=1)
        if payslip_done:
            raise UserError(
                _('The payslip for this period is already confirmed for '
                  'employee "%s". No new advance can be created for a '
                  'closed period.') % self.employee_id.name
            )

        # Aggregate ceiling check.
        self._check_advance_ceiling()

        self.state = 'waiting_approval'

    def approve_request_acc_dept(self):
        """Accounting department final approval — posts the journal entry.

        Checks performed:
        1. Advance amount must be > 0.
        2. Debit account, Credit account, and Journal must be filled.
        3. Aggregate ceiling check (second gate — in case contract/structure
           changed between HR approval and accounting approval).

        Journal entry posted:
            DR  Debit Account (Employee Advance Account)   advance amount
            CR  Credit Account (Cash / Bank)               advance amount

        partner_id is NOT yet attached to move lines in Milestone 1.
        It will be added in Milestone 2 when we wire up the employee
        sub-ledger properly.
        """
        self.ensure_one()

        if not self.advance or self.advance <= 0:
            raise UserError(_('Please enter a valid advance amount greater than zero.'))

        if not self.debit or not self.credit or not self.journal:
            raise UserError(
                _('Please fill in the Debit Account, Credit Account, and '
                  'Journal before approving.')
            )

        # Second ceiling check — accounting approval is the financial gate.
        self._check_advance_ceiling()

        today = time.strftime('%Y-%m-%d')
        line_ids = [
            # Debit line — Employee Advance Account
            (0, 0, {
                'name': _('Salary Advance - %s') % self.employee_id.name,
                'account_id': self.debit.id,
                'journal_id': self.journal.id,
                'date': today,
                'debit': self.advance if self.advance > 0.0 else 0.0,
                'credit': -self.advance if self.advance < 0.0 else 0.0,
            }),
            # Credit line — Cash / Bank
            (0, 0, {
                'name': _('Salary Advance - %s') % self.employee_id.name,
                'account_id': self.credit.id,
                'journal_id': self.journal.id,
                'date': today,
                'debit': -self.advance if self.advance < 0.0 else 0.0,
                'credit': self.advance if self.advance > 0.0 else 0.0,
            }),
        ]

        move_vals = {
            'narration': _('Salary Advance of %s') % self.employee_id.name,
            'ref': self.name,
            'journal_id': self.journal.id,
            'date': today,
            'line_ids': line_ids,
        }

        move = self.env['account.move'].create(move_vals)
        move.action_post()

        self.state = 'approve'
        return True