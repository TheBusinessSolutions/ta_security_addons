from odoo import api, models, fields
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    barcode = fields.Char(string='Barcode')

    @api.onchange('barcode')
    def onchange_barcode(self):
        if self.barcode:
            domain = []
            if self.env.user.company_id.scan_type == 'barcode':
                domain.append(('barcode', '=', self.barcode))
            elif self.env.user.company_id.scan_type == 'code':
                domain.append(('default_code', '=', self.barcode))
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
                order_line[0]._check_product_validity()
                order_line[0].product_qty += 1.0
            else:
                new_line = self.order_line.new({
                    'product_id': product_id.id,
                    'product_qty': 1
                })
                self.order_line += new_line
                for line in self.order_line:
                    line._check_product_validity()
                    line.onchange_product_id()
                    # line._compute_price_unit_and_date_planned_and_name()

            self.barcode = ""
