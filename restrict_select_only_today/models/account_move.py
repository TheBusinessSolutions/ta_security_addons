from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.constrains('date')
    def _check_date_restriction(self):
        # Allow users in the custom group or System Administrators to bypass
        if self.env.user.has_group('restrict_select_only_today.group_allow_custom_invoice_date'):
            return

        today = date.today()
        for record in self:
            # Only apply restriction if the record date is actually being set/changed
            if record.date and record.date != today:
                raise ValidationError(
                    _("You are restricted to using today's date (%s). "
                      "Please contact your administrator to change the date.") % today
                )