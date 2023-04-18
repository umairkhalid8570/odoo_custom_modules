# -*- coding: utf-8 -*-
{
    'name': 'POS Session Timeout',
    'version': '15.0.1.0',
    'category': 'Sales',
    'depends': ['pos_hr'],
    'description': '''
    Session timeout in each sale order completed.
        ''',
    'author': "Umair Khalid",
    'Email': 'umair.khalid8570@gmail.com',
    'data': [
             'views/pos_config_view.xml'
             ],
    'assets': {
        'point_of_sale.assets': [
            'pos_session_timeout/static/src/js/ReceiptScreen.js',
            'pos_session_timeout/static/src/js/poscomponent.js',
        ]
    },
    'installable': True,
    'application': False,
}
