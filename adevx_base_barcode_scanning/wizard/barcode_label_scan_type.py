from odoo import api, fields, models


class BarcodeLabelScanType(models.TransientModel):
    """
    .. note:: We generate this class to remotely control res.company scan_type
    """
    _name = 'barcode.label.scan.type'
    _description = 'Barcode Label Scan Type'

    scan_type = fields.Selection(
        string='Scan Type', selection=[('code', 'Code'), ('barcode', 'Barcode')],
        required=True,
        default=lambda self: self.env.user.company_id.scan_type)

    def update_company_scan_type(self):
        self.env.user.company_id.write({
            'scan_type': self.scan_type
        })


