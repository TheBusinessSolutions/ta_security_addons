from odoo import fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"

    brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['brand_id'] = "t.brand_id"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """, t.brand_id"""
        return res

