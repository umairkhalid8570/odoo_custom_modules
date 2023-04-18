# -*- coding: utf-8 -*-
{
    'name': "POS Customizations",
    'version': '14.0.1.0.0',
    'category': 'Point of Sale',
    'summary': "POS Customization",
    'author': "Telenoc Group",
    'website': "http://telenoc.org",

    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/pos_assets.xml',

    ],
    'assets': {
        'web.assets_qweb': [
             'itelenoc_pos_ext/static/src/xml/**/*',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
}
