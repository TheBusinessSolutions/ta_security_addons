from odoo import http
from odoo.http import request, content_disposition
import io
import xlsxwriter
from datetime import datetime
class InventoryValuationXlsxController(http.Controller):

    @http.route('/inventory_valuation/xlsx', type='http', auth='user')
    def generate_inventory_valuation_xlsx(self, **kwargs):
        wizard_id = int(kwargs.get('wizard_id'))
        # Fetch report data
        report_model = request.env['report.windx_inventory_valuation_report.report_inventory_valuation']
        data = report_model._get_report_values([wizard_id])
        wizard = data.get('docs')[0]
        # Create worksheet in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Inventory Valuation')
        # Styles
        style_report_title = workbook.add_format({'bold': True,'bg_color': '#d9d9d9', 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'font_size': 14, 'border': 1})
        style_table_header = workbook.add_format({'bold': True, 'bg_color': '#d9d9d9', 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': 1})
        style_number_cell = workbook.add_format({'num_format': '#,##0.00', 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        style_total_row = workbook.add_format({'bold': True, 'bg_color': '#d9d9d9', 'num_format': '#,##0.00', 'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        style_cell_default = workbook.add_format({'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        # Header
        row, col = 0, 0
        sheet.merge_range(row, col, row, col + 9, 'Inventory Valuation Report', style_report_title)
        row += 2
        sheet.write_row(row, col, ['Company', 'Warehouse', 'Start Date', 'End Date'], style_table_header)
        row += 1
        sheet.write_row(row, col, [request.env.company.name, ", ".join(wizard.warehouse_ids.mapped('name')),
                        wizard.start_date.strftime('%Y-%m-%d'), wizard.end_date.strftime('%Y-%m-%d')],style_cell_default)
        row += 2
        # Write table headers
        def write_table_headers(start_row, locational=False):
            headers = ['Beginning', 'Received', 'Sales', 'Internal', 'Adjustments', 'Ending']
            static = ['Product', 'Costing Method']
            if locational: static.append('Location')
            col_idx = 0
            for title in static:
                sheet.write(start_row, col_idx, title, style_table_header)
                col_idx += 1
            for group in headers:
                sheet.merge_range(start_row, col_idx, start_row, col_idx + 1, group, style_table_header)
                col_idx += 2
            start_row += 1
            col_idx = 0
            for _ in static:
                sheet.write(start_row, col_idx, '', style_cell_default)
                col_idx += 1
            for _ in headers:
                sheet.write_row(start_row, col_idx, ['Qty', 'Value'], style_table_header)
                col_idx += 2
            return start_row + 1
        # Write main product line
        def write_product_line(row, product, locational=False, col=0):
            sheet.write(row, col, product['name'], style_cell_default)
            sheet.write(row, col + 1, product['costing_method'], style_cell_default)
            check = 1 if locational else 0
            style = style_total_row if locational else style_number_cell
            if locational: sheet.write(row, col + 2, '', style_cell_default)
            sheet.write_row(row, col + check + 2, [
                product['totals']['begin_qty'], product['totals']['begin_value'],
                product['totals']['received_qty'], product['totals']['received_value'],
                product['totals']['sales_qty'], product['totals']['sales_value'],
                product['totals']['internal_qty'], product['totals']['internal_value'],
                product['totals']['adjustment_qty'], product['totals']['adjustment_value'],
                product['totals']['ending_qty'], product['totals']['ending_value']
            ], style)
            return row + 1
        # Write product info for each location
        def write_location_line(row, location_product, col=0):
            sheet.merge_range(row, col, row, col + 1, '', style_cell_default)
            sheet.write(row, col + 2, location_product['location'], style_cell_default)
            sheet.write_row(row, col + 3, [
                location_product['begin_qty'], location_product['begin_value'],
                location_product['received_qty'], location_product['received_value'],
                location_product['sales_qty'], location_product['sales_value'],
                location_product['internal_qty'], location_product['internal_value'],
                location_product['adjustment_qty'], location_product['adjustment_value'],
                location_product['ending_qty'], location_product['ending_value']
            ], style_number_cell)
            return row + 1
        # Write total qty & value for each category
        def write_category_total(row, subtotal, locational=False, col=0):
            check = 1 if locational else 0
            sheet.merge_range(row, col, row, col + check + 1, 'Total', style_total_row)
            sheet.write_row(row, col + check + 2, [
                subtotal['begin_qty'], subtotal['begin_value'],
                subtotal['received_qty'], subtotal['received_value'],
                subtotal['sales_qty'], subtotal['sales_value'],
                subtotal['internal_qty'], subtotal['internal_value'],
                subtotal['adjustment_qty'], subtotal['adjustment_value'],
                subtotal['ending_qty'], subtotal['ending_value']
            ], style_total_row)
            return row + 1
        # Write total qty & value for all products if not group by category
        def write_grand_total(row, grand_total, locational=False, col=0):
            check = 1 if locational else 0
            sheet.merge_range(row, col, row, col + check + 1, 'Total', style_total_row)
            sheet.write_row(row, col + check + 2, [
                grand_total.get('begin_qty', 0.0), grand_total.get('begin_value', 0.0),
                grand_total.get('received_qty', 0.0), grand_total.get('received_value', 0.0),
                grand_total.get('sales_qty', 0.0), grand_total.get('sales_value', 0.0),
                grand_total.get('internal_qty', 0.0), grand_total.get('internal_value', 0.0),
                grand_total.get('adjustment_qty', 0.0), grand_total.get('adjustment_value', 0.0),
                grand_total.get('ending_qty', 0.0), grand_total.get('ending_value', 0.0)
            ], style_total_row)
            return row + 1
        # Process content
        locational = data.get('location')
        check = 1 if locational else 0
        row = write_table_headers(row, locational)
        if data.get('group_by_categories'):
            for category in data['products']:
                sheet.merge_range(row, col, row, col + check + 13, category['category_name'], style_table_header)
                row += 1
                for product in category['products']:
                    row = write_product_line(row, product, locational)
                    if locational:
                        for loc in product.get('sub_products', []):
                            row = write_location_line(row, loc)
                row = write_category_total(row, category['subtotal'], locational)
        else:
            for product in data['products']:
                row = write_product_line(row, product, locational)
                if locational:
                    for loc in product.get('sub_products', []):
                        row = write_location_line(row, loc)
            row = write_grand_total(row, data.get('grand_total', {}), locational)

        workbook.close()
        output.seek(0)
        filename = 'Inventory_Valuation_%s.xlsx' % datetime.today().strftime('%Y%m%d_%H%M%S')
        return request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition(filename))
            ]
        )