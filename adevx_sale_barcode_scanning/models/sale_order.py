from odoo import api, models, fields
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    barcode = fields.Char(string='Barcode')

    @api.onchange('barcode')
    def onchange_barcode(self):
        if self.barcode:
            if self.env.user.company_id.scan_type == 'barcode':
                domain = [('barcode', '=', self.barcode)]
            elif self.env.user.company_id.scan_type == 'code':
                domain = [('default_code', '=', self.barcode)]
            else:
                raise UserError('Unknown Company Scan Type !!')

            product_id = self.env['product.product'].search(domain)
            if not product_id:
                if self.env.user.company_id.scan_type == 'barcode':
                    raise UserError("Unknown Barcode: %s" % str(self.barcode))
                elif self.env.user.company_id.scan_type == 'code':
                    raise UserError("Unknown Default Code: %s" % str(self.barcode))

            if any(line for line in self.order_line if line.product_id.id == product_id.id):
                order_line = self.order_line.filtered(lambda l: l.product_id.id == product_id.id)
                order_line[0].product_uom_qty += 1.0
            else:
                new_line = self.order_line.new({
                    'product_id': product_id.id,
                    'product_uom_qty': 1
                })
                self.order_line += new_line
                for line in self.order_line:
                    line._compute_custom_attribute_values()
                    line._compute_no_variant_attribute_values()
                    line._compute_price_unit()
                    line._onchange_product_id_warning()

            self.barcode = ""
