# -*- coding: utf-8 -*-

{
    'name': 'Candex HR',
    'category': 'Human Resources',
    'summary': 'Centralize employee information',
    'description': "",
    'depends': ['hr', 'hr_recruitment', 'survey'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_recruitment_views.xml',
    ],
    'application': True,
    'installable': True,
}
