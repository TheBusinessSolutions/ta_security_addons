# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def action_open_gl_account(self):
        domain = [('id', '=', self.default_account_id.id)]
        return {
            'res_model': 'account.account',
            'view_mode': 'tree',
            'view_id': self.env.ref('devnix_gl_account_balance.account_account_view_tree').id,
            'type': 'ir.actions.act_window',
            'domain': domain,
            'context': {'create': False, 'edit': False}
        }

    gl_balance = fields.Float(
        string='Gl balance',
        required=False, compute='_compute__gl_balance')

    def _compute__gl_balance(self):
        for rec in self:
            rec.gl_balance = rec.default_account_id.current_balance
