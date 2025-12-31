from odoo import models, api
from collections import defaultdict
from datetime import datetime, time
class ReportInventoryValuation(models.AbstractModel):
    _name = 'report.windx_inventory_valuation_report.report_inventory_valuation'
    _description = 'Report Inventory Valuation'
    _table = 'report_inventory_valuation'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['inventory.valuation.wizard'].browse(docids)
        if not docs: return {}
        wizard = docs[0]
        cost_method_dict = dict(self.env['product.template'].fields_get(['cost_method'])['cost_method']['selection'])
        stock_location_ids = self._get_stock_locations(wizard)
        products = self._get_products(wizard, stock_location_ids, cost_method_dict)
        grand_total = {
            'begin_qty': 0.0, 'begin_value': 0.0,
            'received_qty': 0.0, 'received_value': 0.0,
            'sales_qty': 0.0, 'sales_value': 0.0,
            'internal_qty': 0.0, 'internal_value': 0.0,
            'adjustment_qty': 0.0, 'adjustment_value': 0.0,
            'ending_qty': 0.0, 'ending_value': 0.0,
        }
        location = True if wizard.location_ids else False
        group_by_categories = True if wizard.group_by_category else False
        # Calculate grand totals or Group products by categories
        if not wizard.group_by_category:
            grand_total = self._calculate_grand_total(products, grand_total)
        else: 
            products = self._group_by_category(products)
        return {
            'doc_ids': docids,
            'doc_model': 'inventory.valuation.wizard',
            'docs': wizard,
            'products': products,
            'group_by_categories': group_by_categories,
            'location': location,
            'grand_total': grand_total
        }

    def _calculate_grand_total(self, products, grand_total):
        totals = defaultdict(float)
        fields = [
            'begin_qty', 'begin_value', 'received_qty', 'received_value',
            'sales_qty', 'sales_value', 'internal_qty', 'internal_value',
            'adjustment_qty', 'adjustment_value', 'ending_qty', 'ending_value'
        ]
        for product in products:
            for field in fields:
                totals[field] += product['totals'][field]
        grand_total.update(totals)
        return grand_total

    def _get_stock_locations(self, wizard):
        locations = self.env['stock.location']
        warehouse_location_ids = []
        for warehouse in wizard.warehouse_ids:
            if warehouse.view_location_id:
                warehouse_location_ids += locations.search([
                    ('usage', '=', 'internal'),
                    ('id', 'child_of', warehouse.view_location_id.id)
                ]).ids
        selected_location_ids = wizard.location_ids.ids
        if wizard.location_ids and wizard.warehouse_ids:
            return list(set(selected_location_ids).intersection(set(warehouse_location_ids)))
        else:
            return warehouse_location_ids

    def _get_products(self, wizard, stock_location_ids, cost_method_selection_dict):
        StockMove = self.env['stock.move']
        Product = self.env['product.product']
        Location = self.env['stock.location']
        # Convert wizard dates to datetime
        start_dt = datetime.combine(wizard.start_date, time.min)
        end_dt = datetime.combine(wizard.end_date, time.max)
        # Get product ids
        domain = [('location_id', 'in', stock_location_ids)]
        product_ids = self.env['stock.quant'].search(domain).mapped('product_id').ids
        if wizard.filter_by == 'product' and wizard.product_ids:
            product_ids = wizard.product_ids.ids
        elif wizard.filter_by == 'category' and wizard.category_ids:
            product_ids = Product.search([
                ('categ_id', 'in', wizard.category_ids.ids)
            ]).ids
        if not product_ids: return []
        products = Product.browse(product_ids)
        tmpl_map = {p.id: p.product_tmpl_id for p in products}
        # Locations dict {id: name}
        locations = {loc.id: loc.display_name for loc in Location.browse(stock_location_ids)}
        # Get all relevant stock moves
        moves = StockMove.search([
            ('product_id', 'in', product_ids),
            ('state', '=', 'done'),
            ('date', '<=', end_dt),
            '|', ('location_id', 'in', stock_location_ids),
                ('location_dest_id', 'in', stock_location_ids),
        ])
        # Grouping stock moves
        move_map = defaultdict(list)
        for m in moves:
            move_map[(m.product_id.id, m.location_id.id, m.location_dest_id.id)].append(m)
        # Initialize product map
        products_map = defaultdict(lambda: {
            'name': '',
            'costing_method': '',
            'category': '',
            'totals': {k: 0.0 for k in [
                'begin_qty', 'begin_value', 'received_qty', 'received_value',
                'sales_qty', 'sales_value', 'internal_qty', 'internal_value',
                'adjustment_qty', 'adjustment_value', 'ending_qty', 'ending_value'
            ]},
            'sub_products': []
        })
        # Process each product × location
        for product in products:
            tmpl = tmpl_map[product.id]
            cost_price = product.standard_price
            prod_line = products_map[product.id]
            prod_line['name'] = product.display_name
            prod_line['costing_method'] = cost_method_selection_dict.get(tmpl.cost_method, 'Unknown')
            prod_line['category'] = tmpl.categ_id.name
            for loc_id, loc_name in locations.items():
                begin_qty = received_qty = sales_qty = internal_qty = adjustment_qty = 0.0
                for (pid, src_id, dest_id), mlist in move_map.items():
                    if pid != product.id:
                        continue
                    for move in mlist:
                        qty = move.quantity
                        date = move.date
                        # Beginning stock
                        if date < start_dt:
                            if dest_id == loc_id:
                                begin_qty += qty
                            if src_id == loc_id:
                                begin_qty -= qty
                        # Received from supplier
                        if start_dt <= date and dest_id == loc_id and move.location_id.usage == 'supplier':
                            received_qty += qty
                        # Sales to customer
                        if start_dt <= date and src_id == loc_id and move.location_dest_id.usage == 'customer':
                            sales_qty += qty
                        # Internal transfers
                        if start_dt <= date and move.location_id.usage == 'internal' and move.location_dest_id.usage == 'internal':
                            if dest_id == loc_id:
                                internal_qty += qty
                            elif src_id == loc_id:
                                internal_qty -= qty
                        # Adjustments
                        if start_dt <= date and move.location_id.usage == 'inventory':
                            if dest_id == loc_id:
                                adjustment_qty += qty
                            elif src_id == loc_id:
                                adjustment_qty -= qty
                # Ending
                ending_qty = begin_qty + received_qty - sales_qty + internal_qty + adjustment_qty
                # Location breakdown
                sub_line = {
                    'location': loc_name,
                    'begin_qty': begin_qty, 'begin_value': begin_qty * cost_price,
                    'received_qty': received_qty, 'received_value': received_qty * cost_price,
                    'sales_qty': sales_qty, 'sales_value': sales_qty * cost_price,
                    'internal_qty': internal_qty, 'internal_value': internal_qty * cost_price,
                    'adjustment_qty': adjustment_qty, 'adjustment_value': adjustment_qty * cost_price,
                    'ending_qty': ending_qty, 'ending_value': ending_qty * cost_price,
                }
                # Add to totals
                for k, v in sub_line.items():
                    if k != 'location':
                        prod_line['totals'][k] += v
                prod_line['sub_products'].append(sub_line)
        return list(products_map.values())

    def _group_by_category(self, products):
        fields = [
            'begin_qty', 'begin_value', 'received_qty', 'received_value',
            'sales_qty', 'sales_value', 'internal_qty', 'internal_value',
            'adjustment_qty', 'adjustment_value', 'ending_qty', 'ending_value'
        ]
        category_dict = defaultdict(lambda: {
            'category_name': '',
            'subtotal': {f: 0.0 for f in fields},
            'products': []
        })
        for prod in products:
            cat = prod['category']
            cat_data = category_dict[cat]
            cat_data['category_name'] = cat
            cat_data['products'].append(prod)
            # Aggregate totals
            for f in fields:
                cat_data['subtotal'][f] += prod['totals'][f]
        return list(category_dict.values())