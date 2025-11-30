# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from lxml import etree
import json


class DataCleaner(models.TransientModel):
    _name = 'data.cleaner'
    _description = 'Data Cleaning Wizard'

    # Fields to select which data to clean
    clean_sales = fields.Boolean("Sales & Transfers")
    clean_purchases = fields.Boolean("Purchases & Transfers")
    clean_transfers = fields.Boolean("Stock Transfers Only")
    clean_invoices = fields.Boolean("Invoices, Payments & Journal Entries")
    clean_journals = fields.Boolean("Journal Entries Only")
    clean_partners = fields.Boolean("Customers & Vendors")
    clean_accounts = fields.Boolean("Chart of Accounts & Accounting Data")
    clean_pos = fields.Boolean("Point of Sale Data")
    clean_projects = fields.Boolean("Projects, Tasks & Timesheets")
    clean_timesheets = fields.Boolean("Timesheets Only")
    clean_boms = fields.Boolean("BOM & Manufacturing Orders")
    clean_all_data = fields.Boolean("All Data")

    # Helper function to execute SQL commands
    def _check_and_execute(self, table):
        query = f"""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        );
        """
        self._cr.execute(query, (table,))
        table_exists = self._cr.fetchone()[0]
        if table_exists:
            delete_query = f"DELETE FROM {table};"
            self._cr.execute(delete_query)

    # Cleaning functions for various data types
    def _clear_sales_data(self):
        tables = [
            "stock_quant", "stock_move_line", "stock_move", "stock_picking",
            "account_partial_reconcile", "account_payment_register",
            "account_move_line", "account_move", "sale_order_line", "sale_order"
        ]
        for table in tables:
            self._check_and_execute(table)

    def _clear_purchase_data(self):
        tables = [
            "stock_quant", "stock_move_line", "stock_move", "stock_picking",
            "account_partial_reconcile", "account_payment_register",
            "account_move_line", "account_move", "purchase_order_line", "purchase_order"
        ]
        for table in tables:
            self._check_and_execute(table)

    def _clear_transfer_data(self):
        tables = ["stock_picking", "stock_move_line", "stock_move", "stock_quant"]
        for table in tables:
            self._check_and_execute(table)

    def _clear_invoice_data(self):
        tables = [
            "account_partial_reconcile", "account_payment_register",
            "account_move_line", "account_move", "account_payment"
        ]
        for table in tables:
            self._check_and_execute(table)

    def _clear_partner_data(self):
        self._cr.execute("""
        DELETE FROM res_partner
        WHERE id NOT IN (
            SELECT partner_id FROM res_users
            UNION SELECT partner_id FROM res_company
        );
        """)

    def _clear_accounting_data(self):
        tables = [
            "account_move_line", "account_move", "account_payment",
            "account_tax", "account_bank_statement_line", "account_bank_statement",
            "pos_payment_method", "account_transfer_model_line", "account_transfer_model",
            "account_journal", "account_account"
        ]
        for table in tables:
            self._check_and_execute(table)

    def _clear_project_data(self):
        tables = [
            "project_task_stage_personal", "project_project_stage",
            "project_tags", "project_project", "project_task",
            "project_milestone", "project_update", "account_analytic_line"
        ]
        for table in tables:
            self._check_and_execute(table)

    def _clear_timesheet_data(self):
        self._check_and_execute("account_analytic_line")

    def _clear_bom_data(self):
        tables = ["mrp_workorder", "mrp_production", "mrp_bom"]
        for table in tables:
            self._check_and_execute(table)

    # Toggle all fields based on "All Data" selection
    @api.onchange('clean_all_data')
    def _toggle_all_fields(self):
        field_names = [
            'clean_sales', 'clean_purchases', 'clean_transfers',
            'clean_invoices', 'clean_journals', 'clean_partners',
            'clean_accounts', 'clean_projects', 'clean_timesheets',
            'clean_boms'
        ]
        for field in field_names:
            setattr(self, field, self.clean_all_data)

    # Main function to perform data cleaning
    def execute_cleaning(self):
        if self.clean_all_data or self.clean_sales:
            self._clear_sales_data()
        if self.clean_all_data or self.clean_purchases:
            self._clear_purchase_data()
        if self.clean_all_data or self.clean_transfers:
            self._clear_transfer_data()
        if self.clean_all_data or self.clean_invoices:
            self._clear_invoice_data()
        if self.clean_all_data or self.clean_partners:
            self._clear_partner_data()
        if self.clean_all_data or self.clean_accounts:
            self._clear_accounting_data()
        if self.clean_all_data or self.clean_projects:
            self._clear_project_data()
        if self.clean_all_data or self.clean_timesheets:
            self._clear_timesheet_data()
        if self.clean_all_data or self.clean_boms:
            self._clear_bom_data()

    # Adjust fields visibility based on installed apps
    def _hide_fields(self, doc, xpath, modifiers_attr):
        nodes = doc.xpath(xpath)
        if nodes:
            modifiers = json.loads(nodes[0].get(modifiers_attr))
            modifiers["invisible"] = True
            nodes[0].set(modifiers_attr, json.dumps(modifiers))

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id, view_type, toolbar, submenu)
        if view_type == 'form':
            installed_modules = {mod.name: mod.state for mod in self.env['ir.module.module'].search([])}
            doc = etree.XML(res['arch'])

            module_field_map = {
                'sale_management': "//field[@name='clean_sales']",
                'purchase': "//field[@name='clean_purchases']",
                'stock': "//field[@name='clean_transfers']",
                'account': [
                    "//field[@name='clean_invoices']", "//field[@name='clean_journals']",
                    "//field[@name='clean_accounts']", "//field[@name='clean_partners']"
                ],
                'project': [
                    "//field[@name='clean_projects']", "//field[@name='clean_timesheets']"
                ],
                'mrp': "//field[@name='clean_boms']"
            }

            for module, xpaths in module_field_map.items():
                if installed_modules.get(module) != 'installed':
                    xpaths = xpaths if isinstance(xpaths, list) else [xpaths]
                    for xpath in xpaths:
                        self._hide_fields(doc, xpath, 'modifiers')

            res['arch'] = etree.tostring(doc, encoding='unicode')

        return res
