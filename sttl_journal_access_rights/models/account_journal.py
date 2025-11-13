from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    journal_users = fields.Many2many('res.users', string="Journal Users")
