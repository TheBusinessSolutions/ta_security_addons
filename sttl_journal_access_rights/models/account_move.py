from odoo import models
from odoo.exceptions import AccessError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def unlink(self):
        if not self.env.user.has_group('sttl_journal_access_rights.delete_journal_user_access'):
            raise AccessError("User don't have rights to delete this record.")

        return super(AccountMove, self).unlink()
