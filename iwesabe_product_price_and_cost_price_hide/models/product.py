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


class ProductTemplate(models.Model):
    _inherit = "product.template"

    hide_price = fields.Boolean(
        string='Hide price',
        compute='_compute_hide_price_cost')
    hide_cost = fields.Boolean(
        string='Hide cost',
        compute='_compute_hide_price_cost')


    @api.depends("standard_price")
    @api.depends_context('uid')
    def _compute_hide_price_cost(self):
        data = self.env['product.hide.access']._get_access_values()
        for product in self:
            product.hide_price = data.get('hide_price', False)
            product.hide_cost = data.get('hide_cost', False)

