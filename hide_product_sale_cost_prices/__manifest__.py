# -*- coding: utf-8 -*-
{
    'name': "hide_product_sale_cost_prices",

    'summary': "Hide product prices based on user settings",

    'description': """
    
This module enhances product data security by allowing administrators to control visibility of product sale and cost prices on product forms, 
based on user group membership.

With this feature, you can assign specific users to “Hide Sale Price” or “Hide Cost Price” groups. 
When users belong to these groups, the corresponding fields (Sale Price and/or Cost Price) are automatically hidden from their product views in Odoo.

    """,

    'author': "Apurva wanjari",
    'license': 'LGPL-3',
    'version': '0.17',

    'depends': ['base', 'product', 'sale_management'],
    'data': [
            'security/security_view.xml',
            'views/product_views.xml'
    ],
    
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
  
}

