from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    scan_type = fields.Selection(related="company_id.scan_type", readonly=False)
