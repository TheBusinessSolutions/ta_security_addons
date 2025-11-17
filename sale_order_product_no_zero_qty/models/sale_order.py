# -*- coding: utf-8 -*-

from odoo import models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        for line in self.order_line:
            if line.product_uom_qty <= 0:
                raise ValidationError('A sales order cannot be validated with products that have zero quantities.')

        return super(SaleOrder, self).action_confirm()
