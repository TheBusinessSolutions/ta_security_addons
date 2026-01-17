{
    'name': 'Workorder Step Restriction',
    'version': '1.0',
    'depends': ['mrp'],
    'category': 'Manufacturing',
    'author': 'Jessy Ledama',
    'website': 'https://simitechnologies.co.ke',
    'description': 'Restrict starting of a Work Order until the previous one is done, or the status is ready.',
    'data': [
        'views/mrp_workorder_views.xml',
        'views/mrp_production_workorder_tree_editable_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'images': ['static/description/images/header.png'],
}
