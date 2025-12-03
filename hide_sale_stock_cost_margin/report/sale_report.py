# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    margin = fields.Float(groups='hide_sale_stock_cost_margin.sale_cost_margin_hide_group')
