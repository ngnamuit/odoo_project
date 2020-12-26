# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Module Management',
    'version': '1.0',
    'category': 'Tools',
    'description': "",
    'website': '',
    'summary': 'Organize your module management with memos',
    'sequence': 45,
    'depends': [
        'web',
        'base',
        'stock',
    ],
    'data': [
        'security/base_group.xml',
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/product_views.xml',
    ],
    'demo': [
        # 'data/note_demo.xml',
    ],
    'qweb': [
        # 'static/src/xml/systray.xml',
    ],
    'test': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
