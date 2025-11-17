{
    'name': 'User Product Template Create Access',
    'version': '17.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Add checkbox to grant product.template create access to inventory users',
    'description': """
        This module adds a checkbox in user settings that grants Create access 
        on product.template to users in the Inventory/User group.
    """,
    'depends': ['base', 'stock'],
    'data': [
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}