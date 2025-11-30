# -*- coding: utf-8 -*-
{
    'name': "Smart Data Cleaner",
    'summary': "A comprehensive tool to clean and reset data across various Odoo modules.",
    'description': """
Smart Data Cleaner
===================
This application allows you to clean and reset data for various Odoo modules like Sales, Purchases, Accounting, Projects, Manufacturing, and more. 

Key Features:
--------------
- Selective or complete data cleanup.
- User-friendly wizard interface for easy usage.
- Ensures safe deletion of linked data.
- Compatible with Odoo 16.

Ideal for developers and administrators who need to reset data during testing or setup.
""",
    'author': 'bst-inn, Amro00743',
    "support": "amro00743@gmail.com",
    'website': 'https://www.linkedin.com/in/amro00743/',
    'category': 'Tools',
    'version': '17.0.1.0.0',
    'license': 'OPL-1',
    'price': 0,
    'currency': "USD",
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/smart_data_cleaner.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'application': True, 
    'installable': True,
    'auto_install': False,
}
