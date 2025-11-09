# -*- coding: utf-8 -*-

{
    'name' : 'User Restriction for Invoice/Bills',
    'version' : '17.0.1.0',
    'summary': 'User Restriction for Invoice/Bills',
    'sequence': 10,
    'description': '''
        User Restriction for Invoice/Bills
    ''',
    'data': [
        'data/journal_group.xml',
        'security/groups.xml',
        'views/account_move_views.xml',
        'views/account_journal_views.xml',
        'security/account_security.xml',
    ],
    'category': 'Accounting/Accounting',
    'depends': ['account'],   
    'installable': True,
    'application': False,
    "price": 0,
    "author": "Silver Touch Technologies Limited",
    "website": "https://www.silvertouch.com/",
    'images': ['static/description/banner.png'],
    "currency": "USD",
    'license': 'LGPL-3',
}
