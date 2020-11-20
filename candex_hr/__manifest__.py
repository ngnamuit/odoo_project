# -*- coding: utf-8 -*-

{
    'name': 'Candex HR',
    'category': 'Human Resources',
    'summary': 'Centralize employee information',
    'description': "",
    'depends': ['hr', 'hr_recruitment', 'survey'],
    'data': [
        'data/mail_data.xml',
        'security/ir.model.access.csv',
        'wizard/hr_views.xml',
        'views/hr_recruitment_views.xml',
    ],
    'application': True,
    'installable': True,
}
