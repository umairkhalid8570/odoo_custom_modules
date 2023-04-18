# -*- coding: utf-8 -*-
{
    'name': "POS Customizations",
    'version': '14.0.1.0.0',
    'category': 'Point of Sale',
    'summary': "POS Customization",
    'author': "Umair Khalid",
    'email': "umair.khalid8570@gmail.com",

    'depends': ['base', 'point_of_sale'],
    'data': [
        # 'views/pos_assets.xml',
        # 'views/product_template.xml',
        'views/pos_config.xml',
        # 'views/res_config_settings.xml',

    ],
    'assets': {
        'web.assets_qweb': [
            # 'ibrahimalquraishi_pos_ext/static/src/xml/**/*',
            # 'ibrahimalquraishi_pos_ext/static/src/xml/Screens/ProductScreen/ControlButtons/PromotionButton.xml',
        ],
        'point_of_sale.assets': [
            'looped_pos_ext/static/src/js/models.js',

        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
}
