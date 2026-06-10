{
    'name': 'Restrict Invoice Date to Today',
    'version': '17.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Restrict invoice date selection to current date only.',
    'description': """
        This module forces all users to use today's date for invoice creation.
        - Users without special permissions are restricted to today's date.
        - Administrators or users with the 'Allow Custom Invoice Date' group can bypass this.
    """,
    'author': 'Business Solutions',
    'website': 'https://www.thebusinesssolutions.net',
    'depends': ['account'],
    'data': [
        'security/security.xml',
    ],
    'installable': True,
    'application': False,
}