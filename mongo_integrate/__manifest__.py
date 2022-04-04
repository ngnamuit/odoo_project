# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'MongoDB Integration',
    'version': '1.0',
    'category': 'Tools',
    'description': "",
    'website': '',
    'summary': '',
    'sequence': 45,
    'depends': [
        'base'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/event_views.xml',
        'views/menu_views.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
