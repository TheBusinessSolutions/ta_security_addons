import json
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        has_group_hide_product = self.env.user.has_group('adevx_product_restrictions.group_product_hide_taps')
        if has_group_hide_product:
            for page in arch.xpath("//page"):
                if page.get('name') in ['pos', 'sales', 'inventory', 'invoicing', 'shop']:
                    page.set("invisible", "1")
                    if not page.get("modifiers"):
                        page.set("modifiers", json.dumps({}))
                    modifiers = json.loads(page.get("modifiers"))
                    modifiers['invisible'] = True
                    page.set("modifiers", json.dumps(modifiers))

        return arch, view
