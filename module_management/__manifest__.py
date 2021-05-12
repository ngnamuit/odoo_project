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
        'account',
        'web',
        'mail',
        'website',
        'base',
        'stock',
        'contacts',
        'crm',
        'project',
        'event',
        'event_sale',
        'sales_team',
        'website',
        'website_slides',
    ],
    'data': [
        'security/base_group.xml',
        'security/ir_rules.xml',
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/res_users_views.xml',
        'views/product_views.xml',
        'views/stock_views.xml',
        'views/survey_views.xml',
        'views/menu_views.xml',
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
