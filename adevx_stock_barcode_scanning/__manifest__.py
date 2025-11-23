{
    'name': 'Stock Barcode Scanning',

    'summary': 'Barcode & Code Scanning In Stock Picking',
    'description': 'Barcode & Code Scanning In  and Stock Picking',

    'author': 'Adevx',
    'category': 'Warehouse',
    "license": "OPL-1",
    'website': 'https://adevx.com',

    'depends': ['stock', 'adevx_base_barcode_scanning'],
    'data': [
        # views
        'views/stock_picking.xml',
    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
