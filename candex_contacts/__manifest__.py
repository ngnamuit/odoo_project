# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# cmd to upgrade module: ./odoo-bin -c /etc/odoo-server.conf -d data_base_name -u module_name

{
    'name': 'Candex Contacts Directory',
    'category': 'Tools',
    'summary': 'Customers, Vendors, Partners,...',
    'description': """
This module will inherit base contacts directory, accessible from your home page.
You can track your vendors, customers and other contacts.
""",
    'depends': ['base', 'mail', 'contacts'],
    'data': [
        'data/contacts_views.xml',
        'views/contact_inherit_views.xml',
        'views/contact_actions_inherit.xml'
    ],
    'application': True,
    'installable': True,
}
