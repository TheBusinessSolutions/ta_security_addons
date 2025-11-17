from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    allow_product_template_create = fields.Boolean(
        string='Allow Product Template Creation',
        default=False,
        help='Grant create access on product.template for inventory users'
    )

    @api.model
    def create(self, vals):
        user = super(ResUsers, self).create(vals)
        if vals.get('allow_product_template_create'):
            user._update_product_template_access()
        return user

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if 'allow_product_template_create' in vals:
            self._update_product_template_access()
        return res

    def _update_product_template_access(self):
        """Update product.template create access based on checkbox"""
        for user in self:
            # Get the stock user group
            stock_user_group = self.env.ref('stock.group_stock_user', raise_if_not_found=False)
            
            if not stock_user_group:
                continue
            
            # Check if user is in inventory user group
            if stock_user_group not in user.groups_id:
                continue
            
            # Get or create the access rule
            model_product_template = self.env['ir.model'].search([('model', '=', 'product.template')], limit=1)
            
            if not model_product_template:
                continue
            
            # Search for existing access rule
            access_rule = self.env['ir.model.access'].search([
                ('model_id', '=', model_product_template.id),
                ('group_id', '=', stock_user_group.id),
                ('name', 'ilike', 'product.template stock user create')
            ], limit=1)
            
            if user.allow_product_template_create:
                # Grant create access
                if not access_rule:
                    # Create new access rule
                    self.env['ir.model.access'].sudo().create({
                        'name': 'product.template stock user create access',
                        'model_id': model_product_template.id,
                        'group_id': stock_user_group.id,
                        'perm_read': True,
                        'perm_write': False,
                        'perm_create': True,
                        'perm_unlink': False,
                    })
                else:
                    # Update existing rule
                    access_rule.sudo().write({'perm_create': True})
            else:
                # Remove create access
                if access_rule:
                    access_rule.sudo().write({'perm_create': False})
