from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError
class InventoryValuationWizard(models.TransientModel):
    _name = 'inventory.valuation.wizard'
    _description = 'Inventory Valuation Wizard'

    start_date = fields.Date(default=lambda self: date.today().replace(day=1), string="Start Date")
    end_date = fields.Date(default=lambda self: date.today(), string="End Date")
    warehouse_ids = fields.Many2many('stock.warehouse', string="Warehouse", required=True)
    location_ids = fields.Many2many(
        'stock.location',
        string='Location',
        domain="[('usage', '=', 'internal')]"
    )
    group_by_category = fields.Boolean(string='Group By Category')
    filter_by = fields.Selection([
        ('product', 'Product'),
        ('category', 'Category')
    ], string="Filter By", default='')
    product_ids = fields.Many2many('product.product', string="Products")
    category_ids = fields.Many2many('product.category', string="Categories")
    location_domain = fields.Char(
        compute='_compute_location_domain',
        store=False,
        invisible=True
    )
    @api.depends('warehouse_ids')
    def _compute_location_domain(self):
        for record in self:
            if not record.warehouse_ids:
                record.location_domain = "[]"
            else:
                warehouse_locations = record.warehouse_ids.mapped('view_location_id')
                location_ids = self.env['stock.location'].search([
                    ('id', 'child_of', warehouse_locations.ids),
                    ('usage', '=', 'internal')
                ]).ids
                record.location_domain = str([('id', 'in', location_ids), ('usage', '=', 'internal')])
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        today = date.today()
        for record in self:
            if record.start_date and record.end_date and record.start_date > record.end_date:
                raise ValidationError(_("End date cannot be before start date."))
            if record.start_date > today or record.end_date > today:
                raise ValidationError(_("Start date and end date cannot be in the future."))

    @api.onchange('warehouse_ids')
    def _onchange_warehouse_ids(self):
        self.location_ids = False

    @api.onchange('filter_by', 'warehouse_ids')
    def _onchange_filter_by(self):
        self.product_ids = False
        self.category_ids = False
        if not self.warehouse_ids:
            return {'domain': {
                'product_ids': [],
                'category_ids': []
            }}

        warehouse_locations = self.warehouse_ids.mapped('view_location_id')
        stock_quants = self.env['stock.quant'].search([
            ('location_id', 'child_of', warehouse_locations.ids)
        ])

        if self.filter_by == 'product':
            product_ids = stock_quants.mapped('product_id').ids
            return {'domain': {'product_ids': [('id', 'in', product_ids)]}}
        elif self.filter_by == 'category':
            category_ids = stock_quants.mapped('product_id.categ_id').ids
            return {'domain': {'category_ids': [('id', 'in', category_ids)]}}
        return {'domain': {
            'product_ids': [],
            'category_ids': []
        }}

    def action_export_pdf(self):
        self.ensure_one()
        action = self.env.ref('windx_inventory_valuation_report.action_inventory_valuation_pdf').report_action(self)
        action['close_on_report_download'] = True
        return action

    def action_export_xlsx(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.report',
            'report_type': 'windx_inventory_valuation_xlsx',
            'context': dict(self.env.context, wizard_id=self.id)
        }
