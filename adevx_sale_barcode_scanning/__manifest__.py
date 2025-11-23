{
    'name': 'Sale Barcode Scanning',

    'summary': 'Barcode & Code Scanning  Sale Order',
    'description': 'Barcode & Code Scanning  Sale Order',

    'author': 'Adevx',
    'category': 'Sales',
    "license": "OPL-1",
    'website': 'https://adevx.com',
    "price": 0,
    "currency": 'USD',

    'depends': ['sale', 'adevx_base_barcode_scanning'],
    'data': [
        # views
        'views/sale_order.xml',

    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
