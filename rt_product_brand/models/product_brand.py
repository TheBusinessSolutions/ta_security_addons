from odoo import api, fields, models


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'
    _order = 'name'

    name = fields.Char('Brand Name', required=True)
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer')
    products_count = fields.Integer(string='Number of products', compute='_compute_products_count')

    @api.depends()
    def _compute_products_count(self):
        product_model = self.env['product.template']
        groups = product_model.read_group(
            [('brand_id', 'in', self.ids)],
            ['brand_id'],
            ['brand_id'],
            lazy=False,
        )
        data = {group['brand_id'][0]: group['__count'] for group in groups}
        for brand in self:
            brand.products_count = data.get(brand.id, 0)
