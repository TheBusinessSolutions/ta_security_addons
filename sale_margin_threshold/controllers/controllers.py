# -*- coding: utf-8 -*-
# from odoo import http


# class PosMarginSale(http.Controller):
#     @http.route('/sale_margin_threshold/sale_margin_threshold', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_margin_threshold/sale_margin_threshold/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_margin_threshold.listing', {
#             'root': '/sale_margin_threshold/sale_margin_threshold',
#             'objects': http.request.env['sale_margin_threshold.sale_margin_threshold'].search([]),
#         })

#     @http.route('/sale_margin_threshold/sale_margin_threshold/objects/<model("sale_margin_threshold.sale_margin_threshold"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_margin_threshold.object', {
#             'object': obj
#         })

