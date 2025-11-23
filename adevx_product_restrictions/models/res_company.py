from odoo import api, fields, models, tools


class ResCompany(models.Model):
    _inherit = 'res.company'

    @tools.ormcache()
    def _get_default_category_id(self):
        return self.env.ref('product.product_category_all')

    product_pos_categ = fields.Boolean(string='Same Product Category & Pos Category', default=True)
    property_valuation = fields.Selection(
        selection=[('manual_periodic', 'Manual'), ('real_time', 'Automated')],
        string='Inventory Valuation', required=True, default='real_time')
    force_valuation = fields.Boolean(string="Force Inventory Valuation", default=True)
    property_cost_method = fields.Selection(
        selection=[('standard', 'Standard Price'),
                   ('fifo', 'First In First Out (FIFO)'),
                   ('average', 'Average Cost (AVCO)')],
        string="Costing Method", required=True, default='standard')
    force_cost_method = fields.Boolean(string="Force Cost Method", default=True)
    restricted_product_type = fields.Selection(
        string="Restricted Product Type",
        selection=lambda self: self.env["product.template"]._fields["detailed_type"].selection,
        required=True,
        default='product'
    )
    force_restricted_type = fields.Boolean(string="Force Restricted Type", default=True)
    categ_id = fields.Many2one(comodel_name="product.category", default=_get_default_category_id,
                               string="Default Product Category")

    available_in_pos = fields.Boolean(string='Available In Pos', default=True)
    force_in_pos = fields.Boolean(string='Force In Pos', default=True)
