from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    # Many2many field to store users explicitly allowed to use this journal.
    journal_users = fields.Many2many('res.users', string="Journal Users")

# class AccountJournal(models.Model):
#     _inherit = "account.journal"

#     journal_users = fields.Many2many('res.users', string="Journal Users")
