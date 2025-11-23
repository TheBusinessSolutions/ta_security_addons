import json
from odoo.exceptions import UserError
from odoo import api, fields, models, Command


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    available_in_pos = fields.Boolean(default=lambda self: self.env.company.available_in_pos)
    categ_id = fields.Many2one('product.category', default=lambda self: self.env.company.categ_id)
    categ_id_domain = fields.Char(
        string="Category Domain", compute="_compute_categ_domain", help="Compute Category Domain")
    detailed_type = fields.Selection(default='product')

    # ============================= Onchange functions ============================= #
    @api.onchange("categ_id")
    def _onchange_categ_id(self):
        if self.env.user.company_id.product_pos_categ:
            pos_categs = self.env['pos.category'].search([('name', '=', self.categ_id.name)])
            if pos_categs:
                self.pos_categ_ids = [Command.set(pos_categs.ids)]
        if self.categ_id.restricted_product_type:
            self.detailed_type = self.categ_id.restricted_product_type

    @api.onchange('pos_categ_ids')
    def _onchange_pos_categ_ids(self):
        if self.env.user.company_id.product_pos_categ:
            if self.pos_categ_ids:
                if self.categ_id.name not in self.pos_categ_ids.mapped('name'):
                    raise UserError('Product Category Should Be in Pos Categories')

    # ============================= Compute functions ============================= #

    @api.depends("detailed_type")
    def _compute_categ_domain(self):
        for rec in self:
            if rec.detailed_type:
                rec.categ_id_domain = [("restricted_product_type", "=", rec.detailed_type)]
            else:
                rec.categ_id_domain = []

    # ============================= Constraint functions ============================= #
    @api.onchange("detailed_type")
    def _check_product_type(self):
        for rec in self:
            if rec.env.user.company_id.force_restricted_type:
                if rec.categ_id.restricted_product_type and rec.detailed_type != rec.categ_id.restricted_product_type:
                    raise UserError(
                        "The product type must be equal to restricted product type defined in selected product category")

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

    @api.model
    def create(self, values):
        if not values.get('available_in_pos'):
            if self.env.user.company_id.force_in_pos and not self.env.user.company_id.available_in_pos:
                values['available_in_pos'] = True

        if not values.get('categ_id'):
            if not self.env.company.categ_id:
                values['categ_id'] = self.env['product.category'].search([], limit=1).id

        return super().create(values)
