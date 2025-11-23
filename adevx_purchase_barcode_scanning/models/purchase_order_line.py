from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderLine(models.Model):
    _name = 'purchase.order.line'
    _inherit = ['purchase.order.line', 'variant.domain.abstract']

    def _calc_variant_domain(self):
        res = super()._calc_variant_domain()
        res.extend([('purchase_ok', '=', True), '|', ('company_id', '=', False),
                    ('company_id', '=', self.order_id.company_id.id)])
        return res

    def _check_product_validity(self):
        domain = self._calc_variant_domain()
        domain.append(("id", "=", self.product_id.id))
        product_id = self.env['product.product'].search(domain)
        if not product_id:
            raise UserError("Product exist in system but not in domain !!")
