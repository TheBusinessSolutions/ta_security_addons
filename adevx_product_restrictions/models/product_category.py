from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_valuation = fields.Selection(
        default=lambda self: str(self.env.user.company_id.property_valuation))
    property_cost_method = fields.Selection(
        default=lambda self: str(self.env.user.company_id.property_cost_method))
    restricted_product_type = fields.Selection(
        string="Restricted Product Type",
        selection=lambda self: self.env["product.template"]._fields["detailed_type"].selection,
        default=lambda self: str(self.env.user.company_id.restricted_product_type),
        required=False,
    )

    _sql_constraints = [("name_unique", "unique(name)", "Name must be unique across the database!")]

    # ============================= Constraint functions ============================= #
    @api.constrains("restricted_product_type")
    def _check_restricted_product_type(self):
        if self.restricted_product_type:
            products = self.env["product.template"].search([
                ("categ_id", "=", self.id), ("detailed_type", "!=", self.restricted_product_type)])
            if products:
                raise UserError("A product (or multiple products) in the category "
                                "have different type than the selected restricted product type")

    @api.onchange('restricted_product_type', 'property_valuation', 'property_cost_method')
    def _check_fields(self):
        if self.env.user.company_id.force_restricted_type:
            if self.restricted_product_type != self.env.user.company_id.restricted_product_type:
                restricted_product_type = dict(
                    self.env.user.company_id._fields['restricted_product_type'].selection) \
                    .get(self.env.user.company_id.restricted_product_type)
                raise UserError('Type Must Be: ' + restricted_product_type)

        if self.env.user.company_id.force_valuation:
            if self.property_valuation != self.env.user.company_id.property_valuation:
                company_property_valuation = dict(
                    self.env.user.company_id._fields['property_valuation'].selection) \
                    .get(self.env.user.company_id.property_valuation)
                raise UserError('Inventory Valuation Must Be: ' + company_property_valuation)

        if self.env.user.company_id.force_cost_method:
            if self.property_cost_method != self.env.user.company_id.property_cost_method:
                company_property_cost_method = dict(
                    self.env.user.company_id._fields['property_cost_method'].selection) \
                    .get(self.env.user.company_id.property_cost_method)
                raise UserError('Costing Method Must Be: ' + company_property_cost_method)

    # ============================= Prepare functions ============================= #
    def _create_update_pos_category(self, old_name=False):
        # Recursive create pos category
        name = old_name if old_name else self.name
        pos_categ_id = self.env['pos.category'].search([('name', '=', name)], limit=1)
        if not pos_categ_id:
            pos_categ_id = self.env['pos.category'].create({'name': name})
        # Update pos category name
        if old_name:
            pos_categ_id.name = self.name
        # Update pos category parent_id
        if self.parent_id:
            pos_parent_id = self.parent_id._create_update_pos_category()
            pos_categ_id.parent_id = pos_parent_id
        else:
            pos_categ_id.parent_id = False

        return pos_categ_id

    # ============================= Built-in functions ============================= #
    @api.model
    def create(self, values):
        res = super(ProductCategory, self).create(values)
        if self.env.user.company_id.product_pos_categ:
            res._create_update_pos_category()
        return res

    def write(self, values):
        for rec in self:
            old_name = rec.name
            super(ProductCategory, rec).write(values)
            if self.env.user.company_id.product_pos_categ and (values.get('name') or values.get("parent_id")):
                rec._create_update_pos_category(old_name)
        return True
