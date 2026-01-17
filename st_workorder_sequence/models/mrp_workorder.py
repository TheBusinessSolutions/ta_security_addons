from odoo import models, api, exceptions, fields
from odoo.exceptions import UserError


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    @api.depends('production_id.workorder_ids.state')
    def _compute_can_start(self):
        for workorder in self:
            previous_wos = workorder.production_id.workorder_ids.filtered(
                lambda wo: wo.workcenter_id.sequence < workorder.workcenter_id.sequence
            )
            workorder.can_start = all(wo.state == 'done' for wo in previous_wos)

    can_start = fields.Boolean(string='Can Start', compute='_compute_can_start')

    def button_start(self):
        for wo in self:
            if wo.state != 'ready':
                raise UserError("You can only start a work order that is in the 'Ready' state.")
        return super().button_start()

