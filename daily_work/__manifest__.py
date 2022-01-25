# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Project - Daily Work',
    'version': '1.0',
    'category': 'Tools',
    'description': "",
    'website': '',
    'summary': '',
    'sequence': 45,
    'depends': [
        'base',
        'project',
    ],
    'data': [
        'views/project_views.xml',
        'views/project_old_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
