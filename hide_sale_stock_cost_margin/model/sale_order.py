# -*- coding: utf-8 -*-
from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    margin = fields.Monetary(groups='hide_sale_stock_cost_margin.sale_cost_margin_hide_group')
    margin_percent = fields.Float(groups='hide_sale_stock_cost_margin.sale_cost_margin_hide_group')


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    purchase_price = fields.Float(groups='hide_sale_stock_cost_margin.sale_cost_margin_hide_group')
