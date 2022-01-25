# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Invoice - Medco',
    'version': '1.0',
    'category': 'Tools',
    'description': "",
    'website': '',
    'summary': '',
    'sequence': 45,
    'depends': [
        'web',
        'sale',
        'account'
    ],
    'data': [
        'views/invoice_report_templates.xml',
        'views/sale_order_vizard.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
