# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Survey Custom',
    'version': '1.0',
    'category': 'Tools',
    'description': "",
    'website': '',
    'summary': '',
    'sequence': 45,
    'depends': [
        'base',
        'web',
        'survey',
    ],
    'data': [
        'data/mail_template_data.xml',
        'views/assets.xml',
        'views/survey_templates.xml',
        'views/survey_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
