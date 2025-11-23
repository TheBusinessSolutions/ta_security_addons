from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Product
    product_pos_categ = fields.Boolean(related="company_id.product_pos_categ", readonly=False)

    property_valuation = fields.Selection(related="company_id.property_valuation", readonly=False)

    force_valuation = fields.Boolean(related="company_id.force_valuation", readonly=False)

    property_cost_method = fields.Selection(related="company_id.property_cost_method", readonly=False)

    force_cost_method = fields.Boolean(related="company_id.force_cost_method", readonly=False)

    restricted_product_type = fields.Selection(related="company_id.restricted_product_type", readonly=False)

    force_restricted_type = fields.Boolean(related="company_id.force_restricted_type", readonly=False)

    categ_id = fields.Many2one(related="company_id.categ_id", readonly=False)

    available_in_pos = fields.Boolean(related="company_id.available_in_pos", readonly=False)
    force_in_pos = fields.Boolean(related="company_id.force_in_pos", readonly=False)

    def set_values(self):
        is_automatic = self.env.user.has_group('stock_account.group_stock_accounting_automatic')
        if is_automatic:
            self.group_stock_accounting_automatic = True
        super().set_values()
