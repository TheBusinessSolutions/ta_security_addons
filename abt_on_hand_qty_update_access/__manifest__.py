# -*- coding: utf-8 -*-

{
    "name": "Update Qty Button Access",
    "author": "AskByte Technolab",
    "summary": """ Controls visibility of the 'Update Quantity' button based on user group access. """,
    "description": """
        When enabled, the "On Hand Qty Update Access" setting allows authorized users 
        to see and use the "Update Quantity" button; otherwise, it is hidden.
    """,
    "category": "Inventory",
    "version": "17.0.1.0",
    "depends": ["stock"],
    "data": [
        "security/group_on_hand_qty_update_access.xml",
        "views/product_views.xml"
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "auto_install": False,
}
