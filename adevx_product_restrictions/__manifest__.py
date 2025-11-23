{
    'name': "Product Restrictions",

    'summary': """Product Supplierinfo Restrictions""",
    'description': """Product Supplierinfo Restrictions - Product Restricted Type - Product Variant Restrictions""",

    'author': 'Adevx',
    'category': 'Warehouse',
    "license": "OPL-1",
    'website': 'https://adevx.com',
    "price": 0,
    "currency": 'USD',

    'depends': ['purchase', 'point_of_sale', 'sale', 'stock_account'],
    'data': [
        # security
        'security/security.xml',
        # Views
        'views/product_template.xml',
        'views/product_product.xml',
        'views/product_category.xml',
        'views/stock_product_reprt.xml',
        'views/res_config_settings.xml',
    ],

    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
