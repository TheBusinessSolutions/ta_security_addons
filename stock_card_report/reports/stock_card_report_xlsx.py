# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from odoo import models
from odoo.addons.report_xlsx_helper.report.report_xlsx_format import (
    FORMATS,
    XLS_HEADERS,
)

# FIXED: Proper logger initialization
_logger = logging.getLogger(__name__)


class ReportStockCardReportXlsx(models.AbstractModel):
    _name = "report.stock_card_report.report_stock_card_report_xlsx"
    _description = "Stock Card Report XLSX"
    _inherit = "report.report_xlsx.abstract"

    def generate_xlsx_report(self, workbook, data, objects):
        self._define_formats(workbook)
        for product in objects.product_ids:
            for ws_params in self._get_ws_params(workbook, data, product):
                ws_name = ws_params.get("ws_name")
                ws_name = self._check_ws_name(ws_name)
                ws = workbook.add_worksheet(ws_name)
                generate_ws_method = getattr(self, ws_params["generate_ws_method"])
                generate_ws_method(workbook, ws, ws_params, data, objects, product)

    def _get_ws_params(self, wb, data, product):
        filter_template = {
            "1_date_from": {
                "header": {"value": "Date from"},
                "data": {
                    "value": self._render("date_from"),
                    "format": FORMATS["format_tcell_date_center"],
                },
            },
            "2_date_to": {
                "header": {"value": "Date to"},
                "data": {
                    "value": self._render("date_to"),
                    "format": FORMATS["format_tcell_date_center"],
                },
            },
            "3_location": {
                "header": {"value": "Location"},
                "data": {
                    "value": self._render("location"),
                    "format": FORMATS["format_tcell_center"],
                },
            },
        }
        initial_template = {
            "1_ref": {
                "data": {"value": "Initial", "format": FORMATS["format_tcell_center"]},
                "colspan": 9,
            },
            "2_balance": {
                "data": {
                    "value": self._render("balance"),
                    "format": FORMATS["format_tcell_amount_right"],
                }
            },
        }
        # FIXED: Added new columns for From/To Location, Source Document, etc.
        stock_card_template = {
            "1_date": {
                "header": {"value": "Date"},
                "data": {
                    "value": self._render("date"),
                    "format": FORMATS["format_tcell_date_left"],
                },
                "width": 15,
            },
            "2_reference": {
                "header": {"value": "Document #"},
                "data": {
                    "value": self._render("reference"),
                    "format": FORMATS["format_tcell_left"],
                },
                "width": 18,
            },
            "3_location_from": {
                "header": {"value": "From"},
                "data": {
                    "value": self._render("location_from"),
                    "format": FORMATS["format_tcell_left"],
                },
                "width": 20,
            },
            "4_location_to": {
                "header": {"value": "To"},
                "data": {
                    "value": self._render("location_to"),
                    "format": FORMATS["format_tcell_left"],
                },
                "width": 20,
            },
            "5_source_doc": {
                "header": {"value": "Source Doc"},
                "data": {
                    "value": self._render("source_document"),
                    "format": FORMATS["format_tcell_left"],
                },
                "width": 15,
            },
            "6_description": {
                "header": {"value": "Description"},
                "data": {
                    "value": self._render("description"),
                    "format": FORMATS["format_tcell_left"],
                },
                "width": 25,
            },
            "7_partner": {
                "header": {"value": "Partner"},
                "data": {
                    "value": self._render("partner"),
                    "format": FORMATS["format_tcell_left"],
                },
                "width": 20,
            },
            "8_input": {
                "header": {"value": "In"},
                "data": {"value": self._render("input")},
                "width": 10,
            },
            "9_output": {
                "header": {"value": "Out"},
                "data": {"value": self._render("output")},
                "width": 10,
            },
            "10_balance": {
                "header": {"value": "Balance"},
                "data": {"value": self._render("balance")},
                "width": 12,
            },
        }

        ws_params = {
            "ws_name": product.name[:31],
            "generate_ws_method": "_stock_card_report",
            "title": "Stock Card - {}".format(product.name),
            "wanted_list_filter": [k for k in sorted(filter_template.keys())],
            "col_specs_filter": filter_template,
            "wanted_list_initial": [k for k in sorted(initial_template.keys())],
            "col_specs_initial": initial_template,
            "wanted_list": [k for k in sorted(stock_card_template.keys())],
            "col_specs": stock_card_template,
        }
        return [ws_params]

    def _stock_card_report(self, wb, ws, ws_params, data, objects, product):
        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(XLS_HEADERS["xls_headers"]["standard"])
        ws.set_footer(XLS_HEADERS["xls_footers"]["standard"])
        self._set_column_width(ws, ws_params)
        
        row_pos = 0
        row_pos = self._write_ws_title(ws, row_pos, ws_params, True)
        
        # Filter Table
        row_pos = self._write_line(
            ws, row_pos, ws_params, col_specs_section="header",
            default_format=FORMATS["format_theader_blue_center"],
            col_specs="col_specs_filter", wanted_list="wanted_list_filter",
        )
        row_pos = self._write_line(
            ws, row_pos, ws_params, col_specs_section="data",
            render_space={
                "date_from": objects.date_from or "",
                "date_to": objects.date_to or "",
                "location": objects.location_id.display_name if objects.location_id else "All Locations",
            },
            col_specs="col_specs_filter", wanted_list="wanted_list_filter",
        )
        row_pos += 1
        
        # Header
        row_pos = self._write_line(
            ws, row_pos, ws_params, col_specs_section="header",
            default_format=FORMATS["format_theader_blue_center"],
        )
        ws.freeze_panes(row_pos, 0)
        
        # Initial Balance
        balance = objects._get_initial(
            objects.results.filtered(lambda l: l.product_id == product and l.is_initial)
        )
        row_pos = self._write_line(
            ws, row_pos, ws_params, col_specs_section="data",
            render_space={"balance": balance},
            col_specs="col_specs_initial", wanted_list="wanted_list_initial",
        )
        
        # Transaction Lines
        product_lines = objects.results.filtered(
            lambda l: l.product_id == product and not l.is_initial
        )
        for line in product_lines:
            balance += line.product_in - line.product_out
            # FIXED: Proper document reference
            reference = line.picking_id.name if line.picking_id else (line.reference or "")
            row_pos = self._write_line(
                ws, row_pos, ws_params, col_specs_section="data",
                render_space={
                    "date": line.date.strftime("%Y-%m-%d %H:%M") if line.date else "",
                    "reference": reference,
                    "location_from": line.location_from or (line.location_id.display_name if line.location_id else ""),
                    "location_to": line.location_to or (line.location_dest_id.display_name if line.location_dest_id else ""),
                    "source_document": line.source_document or "",
                    "description": line.description or "",
                    "partner": line.partner_id.name if line.partner_id else "",
                    "input": line.product_in or 0,
                    "output": line.product_out or 0,
                    "balance": balance,
                },
                default_format=FORMATS["format_tcell_amount_right"],
            )