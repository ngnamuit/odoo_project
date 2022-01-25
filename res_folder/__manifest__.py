# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Res Folder - Upload file to google storage',
    'version': '1.0',
    'category': 'Tools',
    'description': "",
    'website': '',
    'summary': '',
    'sequence': 45,
    'depends': [
        'project',
    ],
    'data': [
        "security/ir.model.access.csv",
        'views/res_folder_views.xml',
        'views/project_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
