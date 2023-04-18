# -*- coding: utf-8 -*-
{
    'name': "HR Employee Customizations",
    'version': '15.0.1.0.0',
    'category': 'HR',
    'summary': "HR Employee Customizations",
    'author': "Umair Khalid",
    'email': "umair.khalid8570@gmail.com",

    'depends': ['base', 'point_of_sale'],
    'data': [
        # 'views/pos_assets.xml',
        # 'views/product_template.xml',
        'views/hr_employee.xml',
        # 'views/res_config_settings.xml',

    ],
    'assets': {
        'web.assets_qweb': [
            # 'ibrahimalquraishi_pos_ext/static/src/xml/**/*',
            # 'ibrahimalquraishi_pos_ext/static/src/xml/Screens/ProductScreen/ControlButtons/PromotionButton.xml',
        ],
        'point_of_sale.assets': [
        #     'looped_pos_ext/static/src/js/models.js',
        #
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
}
