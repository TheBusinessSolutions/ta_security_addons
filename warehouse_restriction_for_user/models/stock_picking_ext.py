from odoo import fields, api, models


class ResUsers(models.Model):
    _inherit = 'stock.picking'

    def _compute_location_id(self):
        return None

    @api.onchange('user_id')
    def get_records(self):
        if self.env.user.has_group('warehouse_restriction_for_user.ware_house_user_restrict'):
            if not self.env.user.restrict_ware_house:
                picking_ids = []
                location_ids = []
                if self.env.user.restrict_operation:
                    for ware in self.env.user.ware_house_picking_type_ids:
                        picking_ids.append(ware.id)
                if self.env.user.restrict_location:
                    for location in self.env.user.allow_location_ids:
                        location_ids.append(location.id)
                return {
                    'domain': {
                        'picking_type_id': [('id', 'in', picking_ids)],
                        'location_id': [('id', 'in', location_ids)],
                        'location_dest_id':[('id', 'in', location_ids)]
                    }
                }
            else:
                destination_ids = []
                loc = []
                pick_id = []
                for des in self.env.user.allowed_ware_house_ids:
                    destination_ids.append(des.id)
                warehouse = self.env['stock.warehouse'].search([('id', 'in', destination_ids)])
                for record in warehouse:
                    location = self.env['stock.location'].search([('warehouse_id', '=', record.id)])
                    picking = self.env['stock.picking.type'].search([('warehouse_id', '=', record.id)])
                    for rec in location:
                        loc.append(rec.id)
                    for pick in picking:
                        pick_id.append(pick.id)
                return {
                    'domain': {
                        'picking_type_id': [('id', 'in', pick_id)],
                        'location_id': [('id', 'in', loc)],
                        'location_dest_id':[('id', 'in', loc)]
                    }
                }
        else:
            picking = []
            picking_ids = self.env['stock.picking.type'].search([])
            for pick in picking_ids:
                picking.append(pick.id)
            locations_ids =[]
            location = self.env['stock.location'].search([])
            for locs in location:
                locations_ids.append(locs.id)
            return {
                'domain': {
                    'picking_type_id': [('id', 'in', picking)],
                    'location_id': [('id', 'in',locations_ids )],
                    'location_dest_id': [('id', 'in', locations_ids)]
                }
            }

