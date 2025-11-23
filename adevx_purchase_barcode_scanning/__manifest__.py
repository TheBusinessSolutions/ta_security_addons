{
    'name': 'Purchase Barcode Scanning',

    'summary': 'Barcode & Code Scanning In Purchase Order',
    'description': 'Barcode & Code Scanning In Purchase Order',

    'author': 'Adevx',
     "category": "Purchases",
    "license": "OPL-1",
    'website': 'https://adevx.com',

    'depends': ['adevx_product_domain_abstract', 'adevx_base_barcode_scanning', 'purchase'],
    'data': [
        # views
        'views/purchase_order.xml',
    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
