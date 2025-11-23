{

    # App information
    'name': 'Product Brand',
    'category': 'Sales',
    'version': '17.0.0.0.0',
    'summary': 'Product Brand',
    'license': 'OPL-1',
    'description': """Product Brand""",

    'price': 0.00,
    'currency': 'USD',

    # Dependencies
    'depends': [
        'product',
        'sale',
        'stock',
        'contacts',
        'purchase',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/product_brand_view.xml',
        'views/product_template.xml',
        'views/product_views.xml',
        'reports/sale_report_view.xml',
        'reports/account_invoice_report_view.xml'
    ],
    "images": ["static/description/main_screenshot.png"],

    # Author
    'author': 'Rooteam',
    'website': 'https://rooteam.com',
    'maintainer': 'Rooteam',

    'installable': True,
}
