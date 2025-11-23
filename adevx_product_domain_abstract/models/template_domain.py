from odoo import api, fields, models
from .variant_domain import VariantDomain


class TemplateDomain(VariantDomain):
    _name = 'template.domain.abstract'

    product_tmpl_domain = fields.Char(string="Product Template Domain", compute="_compute_tmpl_domain")

    def _calc_tmpl_domain_depends(self):
        return self._calc_variant_domain_depends()

    def _calc_tmpl_domain(self):
        variant_domain = self._calc_variant_domain()
        product_tmpl_ids = self.env['product.product'].sudo().search(variant_domain).mapped('product_tmpl_id').ids
        return [('id', 'in', product_tmpl_ids)]

    @api.depends(lambda self: self._calc_tmpl_domain_depends())
    def _compute_tmpl_domain(self):
        for rec in self:
            rec.product_tmpl_domain = rec._calc_tmpl_domain()
