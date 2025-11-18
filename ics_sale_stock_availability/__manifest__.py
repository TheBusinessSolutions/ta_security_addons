{
    'name': 'Stock Availability in Sales Order',
    'version': '17.0.0.1.0',
    'summary': 'Display stock availability of products in different locations within the sales order lines.',
    'description': """
        This module allows users to see the availability of products in different stock locations directly within the sales order lines.
        Key Features:
        - Display stock availability in sales order lines.
        - Fetch real-time stock quantities from internal locations.
    """,
    'author': 'iCloud Solutions',
    'website': 'https://icloud-solutions.net',
    'category': 'Sales',
    'license': 'OPL-1',
    'price': 0,
    'currency': 'EUR',
    'depends': ['sale_management', 'stock'],
    'data': [
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'images': ['static/description/thumbnail.png'],
    'application': False,
    'auto_install': False,
}
