# Copyright 2020-2023 Sodexis
# License OPL-1 (See LICENSE file for full copyright and licensing details).

{
    "name": "Account Move Reset Button",
    "summary": """
        This module create a user group called "Can reset account move".
        Only the members of that group will see the "Reset to Draft button".
    """,
    "version": "17.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://sodexis.com/",
    "author": "Sodexis",
    "license": "OPL-1",
    "installable": True,
    "depends": [
        "account",
    ],
    "data": [
        "security/security_view.xml",
        "views/account_move_view.xml",
    ],
    "images": ["images/main_screenshot.jpg"],
    "live_test_url": "https://sodexis.com/odoo-apps-store-demo",
}
