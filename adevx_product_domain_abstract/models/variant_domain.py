from odoo import api, fields, models, _


class VariantDomain(models.AbstractModel):
    _name = 'variant.domain.abstract'
    _description = 'Variant Domain'

    product_variant_domain = fields.Char(string="Product Variant Domain", compute="_compute_variant_domain")

    def _calc_variant_domain_depends(self):
        # Add code here
        return []

    def _calc_variant_domain(self):
        # Add code here
        return []

    @api.depends(lambda self: self._calc_variant_domain_depends())
    def _compute_variant_domain(self):
        for rec in self:
            rec.product_variant_domain = rec._calc_variant_domain()
