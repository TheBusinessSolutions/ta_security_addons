from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    scan_type = fields.Selection(string="Scan Type",
                                 selection=[('barcode', 'Barcode'), ('code', 'Code')],
                                 default='barcode')
