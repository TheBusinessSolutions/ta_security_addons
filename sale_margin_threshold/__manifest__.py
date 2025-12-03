# -*- coding: utf-8 -*-
{
    'name': "Sale Margin Threshold",

    'summary': "Ensure products are sold above their minimum price with margin checks in sale orders.",

    'description': """
        The Sale Margin Threshold module ensures that each product is sold at a price that covers its cost and desired profit margin. 
        If a product is sold below its minimum price in a Sale order, 
        the system triggers a warning, helping businesses maintain profitability and prevent underpricing.
    """,

    'author': "Doodex",
    'website': "https://www.doodex.net",
    'license': "AGPL-3",
    'category': 'Sales',
    'version': '17.0.1.0',

    'depends': [
        'base', 
        'product', 
        'sale', 
        'stock_account'
    ],

    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/products.xml',
        'views/res_config_settings.xml',
        'views/sale_order.xml',
        'wizard/sale_confirmation.xml',
        'wizard/wizard_margin_product.xml',
    ],

    'assets': {
        'sale_margin_threshold._assets_sale': [
            'sale_margin_threshold/static/src/**/*', 
        ]
    },
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
    'installable': True,
    'images': ["static/description/banner.png"],
} 