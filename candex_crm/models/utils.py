import logging
import ast
from odoo import api, fields, models, registry, _

NAME_TITLE = [
    ('mr', 'Mr'),
    ('mrs', 'Mrs'),
    ('miss', 'Miss'),
    ('ms', 'Ms')
]


def get_name_title(self):
    icp = self.env['ir.config_parameter'].sudo()
    name_titles = icp.get_param("NAME_TITLE", default=[])
    if name_titles:
        name_titles = ast.literal_eval(name_titles)
        return name_titles
    else:
        return NAME_TITLE

