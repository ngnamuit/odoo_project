# -*- coding: utf-8 -*-
{
    'name': "Medco Custom1",
    'summary': 'Medco Custom1',
    'description': """
    """,
    'author': "EMSG Team",
    'website': "https://enmasys.com/",
    'category': 'Accounting/Accounting',
    'version': '14.0.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/kind_of_dossier.xml',
        'views/kind_of_variation.xml',
        'views/manufactory_line.xml',
        'views/project_info_line.xml',
        'views/project_inherit.xml',
        'views/account_move_line_inherit.xml',
        'views/sale_order_line_inherit.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
