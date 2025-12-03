# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    price_margin = fields.Float(groups='hide_sale_stock_cost_margin.sale_cost_margin_hide_group')
