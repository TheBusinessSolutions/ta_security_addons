{
    'name': 'Account Move User Access',
    'version': '17.0.1.0.0',
    'summary': 'Control user access to own or all invoices, bills, payments and journal entries.',
    'description': """
Account Move User Access

This module provides structured security control over Accounting documents.

It allows administrators to assign users one of two access levels:

1. Own Documents:
   - User can see and manage only invoices, vendor bills,
     journal entries, and payments assigned to or created by them.

2. All Documents:
   - User can see and manage all accounting documents.

Supported Documents:
- Customer Invoices
- Vendor Bills
- Journal Entries
- Payments

This module is designed for Odoo 17 Community Edition
and follows Odoo's standard security architecture.

Ideal for accounting teams where document visibility
must be controlled per responsible user.
    """,
    'author': 'Business Solutions',
    'website': 'https://www.thebusinesssolutions.net',
    'support': 'sales@thebusinesssolutions.net',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}