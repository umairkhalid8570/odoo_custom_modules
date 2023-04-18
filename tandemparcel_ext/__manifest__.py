{
    'name': 'Nova Poshta Global',
    'Version': '15.0.1.0.0',
    'summary': 'Subscription Package Management Module For Odoo15 Community',
    'description': 'Subscription Package Management Module For Odoo15 Community',
    'category': 'Sales',
    'author': 'Umair Khalid',
    'email': 'umair.khalid8570@gmail.com',
    'depends': ['base', 'website'],
    'data': [
        # 'views/data.xml',
        'security/ir.model.access.csv',
        'views/form.xml',
        'views/form_success.xml',
        'views/tandem_quotaton_request.xml',
        'views/data.xml',
        'views/form_response.xml'


    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
