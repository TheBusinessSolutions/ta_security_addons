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
from odoo import models, _


class HrPayslip(models.Model):
    """Extends hr.payslip with two Milestone 3 behaviours:

    1. get_inputs(): injects the TOTAL of all outstanding unpaid approved
       advances into the SAR input line so the accountant sees the correct
       accumulated figure in Other Inputs when preparing the payslip.

    2. action_payslip_done(): after calling super (which posts the payslip
       accounting move), we:
         a. Stamp work_contact_id as partner_id on every line of the payslip
            journal entry that belongs to the employee's advance account,
            so the move line is traceable per employee — consistent with
            how the original advance entry was posted in Milestone 2.
         b. Mark all unpaid approved advances for this employee as is_paid=True
            and link them to this payslip, closing them out.
    """
    _inherit = 'hr.payslip'

    # -------------------------------------------------------------------------
    # get_inputs — inject accumulated outstanding advance total into SAR line
    # -------------------------------------------------------------------------
    def get_inputs(self, contract_ids, date_from, date_to):
        """Override to populate the SAR (Salary Advance Recovery) input line
        with the SUM of ALL outstanding unpaid approved advances for the
        employee — regardless of when each advance was requested.

        Original behaviour: only advances whose date fell in the same calendar
        month as date_from were considered, and only one advance could exist
        at a time anyway.

        Milestone 3 behaviour:
          • Filter: state='approve' AND is_paid=False
          • No date restriction — all open advances are included
          • The total is the number the accountant will see (and can adjust)
            in the Other Inputs section of the payslip form
        """
        res = super().get_inputs(contract_ids, date_from, date_to)

        # Resolve employee from contract list or from the payslip itself.
        employee = (
            self.env['hr.contract'].browse(contract_ids[0].id).employee_id
            if contract_ids
            else self.employee_id
        )
        if not employee:
            return res

        # All approved, not-yet-paid advances for this employee.
        unpaid_advances = self.env['salary.advance'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'approve'),
            ('is_paid', '=', False),
        ])

        if not unpaid_advances:
            return res

        total_outstanding = sum(unpaid_advances.mapped('advance'))

        # Inject into the SAR input line.
        # SAR is the salary rule input code defined in hr_salary_rule_data.xml.
        # get_inputs() has already built the res list with a 0-amount SAR line;
        # we simply set its amount to the accumulated total.
        for result in res:
            if result.get('code') == 'SAR' and total_outstanding > 0:
                result['amount'] = total_outstanding
                break

        return res

    # -------------------------------------------------------------------------
    # action_payslip_done — mark advances paid + fix partner on payslip move
    # -------------------------------------------------------------------------
    def action_payslip_done(self):
        """Override to run post-confirmation logic after the payslip is confirmed.

        Step 1 — call super() to let Odoo confirm the payslip and post the
                  accounting journal entry (the payslip move).

        Step 2 — attach work_contact_id as partner_id on every move line in
                  the payslip journal entry. This ensures the employee is
                  visible as the partner on ALL payslip accounting lines,
                  consistent with the advance journal entry posted in
                  Milestone 2.

        Step 3 — find all outstanding unpaid advances for this employee,
                  mark is_paid=True and link payslip_id to this payslip.
                  This closes them out so they will not be picked up by
                  get_inputs() in any future payslip.

        Note on the SAR amount: the accountant enters (or adjusts) the SAR
        amount manually in Other Inputs before confirming. We trust whatever
        amount was entered — we do not re-validate it here. The ceiling check
        already ran at approval time.
        """
        # Step 1 — standard Odoo payslip confirmation + move posting.
        result = super().action_payslip_done()

        for payslip in self:
            employee = payslip.employee_id
            partner = employee.work_contact_id

            # ------------------------------------------------------------------
            # Step 2 — attach employee partner to all payslip move lines.
            #
            # The payslip move is payslip.move_id (set by super()).
            # We write partner_id on lines that don't already have a partner
            # (some lines like tax lines may already carry a different partner).
            # We only touch lines that are unset so we don't override bank/
            # tax partners inadvertently.
            # ------------------------------------------------------------------
            if payslip.move_id and partner:
                lines_without_partner = payslip.move_id.line_ids.filtered(
                    lambda l: not l.partner_id
                )
                if lines_without_partner:
                    # move is already posted — we need to temporarily reset
                    # it to draft to allow line edits, then re-post.
                    payslip.move_id.button_draft()
                    lines_without_partner.write({'partner_id': partner.id})
                    payslip.move_id.action_post()

            # ------------------------------------------------------------------
            # Step 3 — close out all outstanding unpaid advances.
            #
            # We mark every approved unpaid advance for this employee as paid
            # and link it to this payslip. The SAR amount the accountant entered
            # may not perfectly equal the sum of individual advances (they could
            # have adjusted it), but we close ALL outstanding advances because
            # the payslip is the settlement event for the full balance.
            # ------------------------------------------------------------------
            unpaid_advances = self.env['salary.advance'].search([
                ('employee_id', '=', employee.id),
                ('state', '=', 'approve'),
                ('is_paid', '=', False),
            ])
            if unpaid_advances:
                unpaid_advances.write({
                    'is_paid': True,
                    'payslip_id': payslip.id,
                })

        return result