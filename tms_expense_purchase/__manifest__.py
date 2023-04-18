# -*- coding: utf-8 -*-
{
    'name': 'TMS Expense Purchase Mechanisms',
    'version': '0.1',
    'summary': 'TMS Expense Purchase Mechanisms',
    # 'category': 'Accounting',
    'author': "iCode",
    'website': 'https://www.icode.by',
    'depends': [
        'great_tms',
        'tms_base',
        'account',
    ],
    'data': [

        # views
        'views/tms_expense_bill_views.xml'
    ],
    'auto_install': False,
    'installable': True,
}
