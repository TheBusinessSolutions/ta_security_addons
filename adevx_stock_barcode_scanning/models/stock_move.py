from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _check_product_validity(self):
        pass

    @api.depends('state', 'picking_id', 'product_id')
    def _compute_is_quantity_done_editable(self):
        for move in self:
            if not move.product_id:
                move.is_quantity_done_editable = False
            elif not move.picking_id.picking_type_code == 'internal' and move.picking_id.state == 'draft':
                move.is_quantity_done_editable = False
            elif move.picking_id.is_locked and move.state in ('done', 'cancel'):
                move.is_quantity_done_editable = False
            elif move.show_details_visible:
                move.is_quantity_done_editable = False
            elif move.show_operations:
                move.is_quantity_done_editable = False
            else:
                move.is_quantity_done_editable = True
