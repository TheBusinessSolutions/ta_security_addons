{
    'name': 'Account Move User Access',
    'version': '17.0.1.0.0',
    'summary': 'Restrict access to invoices, bills, payments and journal entries by user',
    'description': 'Allows users to see only their own sales/purchase invoices, payments, and journal entries. Admins or users in the "All Documents" group can see everything.',
    'author': 'Business Solutions',
    'website': 'www.thebusinesssolutions.net',
    'support': 'sales@thebusinesssolutions.net',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'depends': ['account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}