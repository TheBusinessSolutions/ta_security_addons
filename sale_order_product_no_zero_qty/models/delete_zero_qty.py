from odoo import models
from odoo.exceptions import UserError
           
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_remove_zero_quantity_lines(self):
        zero_quantity_lines = self.order_line.filtered(lambda line: line.product_uom_qty == 0)

        if not zero_quantity_lines:
            raise UserError("There are no lines with zero quantity to delete.")

        zero_quantity_lines.unlink()
