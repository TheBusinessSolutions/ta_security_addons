# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<https://www.iwesabe.com>).
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL-3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL-3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL-3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "iWesabe Product Price and Cost Price Hide",
    'version': '17.0.0.1',
    'author': 'iWesabe',
    'summary': """
        Product Price and Cost Price Hide
        """,
    'description': """
        Product Price and Cost Price Hide
    """,
    'website': 'https://www.iwesabe.com/',
    'license': 'LGPL-3',
    'category': 'Product',
    'depends': ['product','stock','base'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_hide_access_view.xml',
        'views/product_views.xml',
    ],
    'images': ['static/description/iWesabe_App_Price_Hide.png'],
    "assets": {

    },
}
