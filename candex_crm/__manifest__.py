# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Candex CRM',
    'category': 'Sales/CRM',
    'summary': 'Track leads and close opportunities',
    'description': "",
    'depends': ['base', 'crm'],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_inherit_views.xml',
    ],
    'application': True,
    'installable': True,
}
