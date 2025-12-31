# -*- coding: utf-8 -*-
{
    'name': "Inventory_valuation_report",

    'description': "",

    'summary': """The Inventory Valuation Report module in Odoo allows you to generate detailed inventory valuation reports in PDF or XLS format, supports multi‑warehouse and multi‑location operations, groups results by product category, and filters easily by product or category for precise stock analysis.
inventory valuation report, inventory report pdf, inventory report xls, valuation report pdf, valuation report xls, real time valuation report, real time stock report, stock valuation report, stock card report, stock card valuation report, odoo inventory report, stock balance report, multi warehouse inventory, multi location inventory, product category report, category wise report, product wise report, inventory group category, inventory filter product, inventory filter category, warehouse stock report, location stock report, stock movement report, stock history report, stock ledger report, stock summary report, stock detail report, stock quantity report, stock value report, stock cost report, stock price report, stock amount report, stock worth report, stock total report, stock daily report, stock monthly report, stock yearly report, stock period report, stock date report, stock time report, stock item report, stock product report, stock goods report, stock material report, stock asset report, stock balance sheet, stock balance list, stock balance data, stock balance info, stock balance detail, stock balance record, stock balance entry, stock balance field, stock balance form, stock balance page, stock balance app, stock balance odoo, stock balance erp, stock balance pos, stock balance api, inventory stock, inventory value, inventory cost, inventory price, inventory amount, inventory worth, inventory total, inventory daily, inventory monthly, inventory yearly, inventory period, inventory date, inventory time, inventory item, inventory product, inventory goods, inventory material, inventory asset, inventory sheet, inventory list, inventory data, inventory info, inventory detail, inventory record, inventory entry, inventory field, inventory form, inventory page, inventory app, inventory odoo, inventory erp, inventory pos, inventory api, valuation stock, valuation value, valuation cost, valuation price, valuation amount, valuation worth, valuation total, valuation daily, valuation monthly, valuation yearly, valuation period, valuation date, valuation time, valuation item, valuation product, valuation goods, valuation material, valuation asset, valuation sheet, valuation list, valuation data, valuation info, valuation detail, valuation record, valuation entry, valuation field, valuation form, valuation page, valuation app, valuation odoo, valuation erp, valuation pos, valuation api, stock report, inventory report, valuation report, real time report, stock card, stock ledger, stock summary, stock detail, stock quantity, stock value, stock cost, stock price, stock amount, stock worth, stock total, stock daily, stock monthly, stock yearly, stock period, stock date, stock time, stock item, stock product, stock goods, stock material, stock asset, stock sheet, stock list, stock data, stock info, stock detail, stock record, stock entry, stock field, stock form, stock page, stock app, stock odoo, stock erp, stock pos, stock api, report pdf, report xls, report excel, report sheet, report list, report data, report info, report detail, report record, report entry, report field, report form, report page, report app, report odoo, report erp, report pos, report api, multi warehouse, multi location, product category, category wise, product wise, group category, filter product, filter category, warehouse report, location report, movement report, history report, ledger report, summary report, detail report, quantity report, value report, cost report, price report, amount report, worth report, total report, daily report, monthly report, yearly report, period report, date report, time report, item report, product report, goods report, material report, asset report, sheet report, list report, data report, info report, detail report, record report, entry report, field report, form report, page report, app report, odoo report, erp report, pos report, api report, inventory, valuation, stock, report, card, ledger, summary, detail, quantity, value, cost, price, amount, worth, total, daily, monthly, yearly, period, date, time, item, product, goods, material, asset, sheet, list, data, info, record, entry, field, form, page, app, odoo, erp, pos, api, warehouse, location, category, filter, group, movement, history, balance.
""",
    'version': "17.0",
    'category': 'Inventory',
    'author': 'Win DX JSC',
    'company': 'Win DX JSC',
    'maintainer': 'Win DX JSC',
    'website': 'https://windx.com.vn',
    'support': 'windxcontact@gmail.com',
    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'product', 'web', 'account'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'report/inventory_valuation_report_templates.xml',
        'report/inventory_valuation_reports.xml',

        'wizards/inventory_valuation_wizard.xml',

        'menu/menus.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'windx_inventory_valuation_report/static/src/js/action_manager.js',
        ],
    },
    'license': 'LGPL-3',
}

