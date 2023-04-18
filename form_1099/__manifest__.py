# -*- coding: utf-8 -*-
{
    'name': 'Form 1099',
    'version': '0.1',
    'summary': 'Form 1099',
    'author': "Umair Khalid",
    'depends': [
        'tms_base',
        'tms_fleet_maintenance',
        'project',
        'hr_contract',
        'tms_expense_extension',
        'tms_contract',

    ],
    'data': [
        'security/ir.model.access.csv',

        'views/accounting_form_1099_view.xml',

        'reports/form_1099_report.xml',

    ],
    # 'qweb': [
    #     "static/src/xml/icode_template_inheri.xml",
    # ],
    'auto_install': False,
    'installable': True,
}
