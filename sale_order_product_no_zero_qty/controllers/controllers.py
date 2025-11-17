# -*- coding: utf-8 -*-
# from odoo import http


# class SaleOrderProductNoCeroQty(http.Controller):
#     @http.route('/sale_order_product_no_cero_qty/sale_order_product_no_cero_qty', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_order_product_no_cero_qty/sale_order_product_no_cero_qty/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_order_product_no_cero_qty.listing', {
#             'root': '/sale_order_product_no_cero_qty/sale_order_product_no_cero_qty',
#             'objects': http.request.env['sale_order_product_no_cero_qty.sale_order_product_no_cero_qty'].search([]),
#         })

#     @http.route('/sale_order_product_no_cero_qty/sale_order_product_no_cero_qty/objects/<model("sale_order_product_no_cero_qty.sale_order_product_no_cero_qty"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_order_product_no_cero_qty.object', {
#             'object': obj
#         })

