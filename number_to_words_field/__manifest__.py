{
    'name': 'Numeric value to words',
    'summary': 'Convert number to words!',
    'description': 'By adding widget="number_to_words" to float fields, the widget will display numeric values as words',
    'author': "cdn.odoo.red",
    'website': "https://cdn.odoo.red/",
    'category': 'Extra Tools',
    'version': '17.0.0.1',
    'depends': ["base"],
    'data': [],

    'assets': {
        'web.assets_backend': [
            'number_to_words_field/static/src/libs/*',
            'number_to_words_field/static/src/number_to_words_field/*',
        ],
    },

    'images': ['static/description/images/words_representation_small.png'],
    'license': 'LGPL-3',
}
