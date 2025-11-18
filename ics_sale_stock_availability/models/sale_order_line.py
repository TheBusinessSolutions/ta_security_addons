from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    stock_availability = fields.Char(
        string="Disponibilité en Stock",
        compute='_compute_stock_availability',
    )

    @api.depends('product_id', 'product_uom_qty')
    def _compute_stock_availability(self):
        for line in self:
            availability = []
            quants = self.env['stock.quant'].search([
                ('product_id', '=', line.product_id.id),
                ('location_id.usage', '=', 'internal')
            ])
            for quant in quants:
                if quant.quantity > 0:
                    availability.append(f"{quant.location_id.display_name}: {quant.quantity}")
            line.stock_availability = ', '.join(availability) if availability else "Indisponible"