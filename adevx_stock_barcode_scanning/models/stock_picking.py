from odoo import api, models, fields
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    barcode = fields.Char(string='Barcode')

    @api.onchange('barcode')
    def onchange_barcode(self):
        if self.barcode:
            where = ""
            if self.env.user.company_id.scan_type == 'barcode':
                where += f"WHERE barcode='{self.barcode}'"
                # domain = [('barcode', '=', self.barcode)]
            elif self.env.user.company_id.scan_type == 'code':
                where += f"WHERE default_code='{self.barcode}'"
                # domain = [('default_code', '=', self.barcode)]
            else:
                raise UserError('Unknown Company Scan Type !!')

            # product_id = self.env['product.product'].search(domain)
            self.env.cr.execute(f"SELECT id FROM product_product {where} LIMIT 1")
            res = self.env.cr.fetchone()
            product_id = False
            if res and res[0]:
                product_id = self.env['product.product'].browse(res[0])

            if not product_id:
                if self.env.user.company_id.scan_type == 'barcode':
                    raise UserError("Unknown Barcode: %s" % str(self.barcode))
                elif self.env.user.company_id.scan_type == 'code':
                    raise UserError("Unknown Default Code: %s" % str(self.barcode))

            if any(line for line in self.move_ids_without_package if line.product_id.id == product_id.id):
                move_line = self.move_ids_without_package.filtered(lambda l: l.product_id.id == product_id.id)
                move_line[0].product_uom_qty += 1.0
                move_line[0]._check_product_validity()
            else:
                new_line = [(0, 0, dict(
                    product_id=product_id.id,
                    name=product_id.display_name,
                    product_uom=product_id.uom_id.id,
                    product_uom_qty=1,
                    partner_id=self.partner_id.id,
                    picking_id=self.id,
                    location_id=self.location_id.id,
                    location_dest_id=self.location_dest_id.id,
                ))]
                self.update(dict(move_ids_without_package=new_line))
                for line in self.move_ids_without_package.filtered(lambda line: line.product_id.id == product_id.id):
                    line._onchange_product_id()
                    line._check_product_validity()

            self.barcode = ""
