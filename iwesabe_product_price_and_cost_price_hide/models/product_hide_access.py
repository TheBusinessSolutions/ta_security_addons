# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<https://www.iwesabe.com>).
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL-3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL-3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL-3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductHideAccess(models.Model):
    _name = 'product.hide.access'
    _description = "Product Hide Access"

    user_ids = fields.Many2many('res.users', 'product_hide_user_rel', 'user_id', 'access_id', string="User(s)")

    hide_price = fields.Boolean(
        string='Hide price',
        default=False)
    hide_cost = fields.Boolean(
        string='Hide cost',
        default=False)

    def _get_access_values(self):
        access = self.search([('user_ids', 'in', self.env.user.id)], limit=1)
        return {
            'hide_price': access.hide_price if access else False,
            'hide_cost': access.hide_cost if access else False
        }

    @api.constrains('user_ids')
    def _check_user_ids(self):
        for rec in self:
            if rec.search([('user_ids', 'in', rec.user_ids.ids), ('id', '!=', rec.id)]):
                raise ValidationError(_('Configuration already assigned to these user(s)'))


