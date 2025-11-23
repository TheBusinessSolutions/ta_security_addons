{
    'name': 'Base Barcode Scanning',

    'summary': 'Barcode & Code Scanning ',
    'description': 'Barcode & Code Scanning',

    'author': 'Adevx',
    'category': 'Hidden',
    "license": "OPL-1",
    'website': 'https://adevx.com',
    "price": 0,
    "currency": 'USD',

    'depends': ['base_setup'],
    'data': [
        # security
        'security/security.xml',
        'security/ir.model.access.csv',
        # wizard
        'wizard/res_config_settings.xml',
        'wizard/barcode_label_scan_type.xml',

    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
