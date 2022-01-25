# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from math import copysign
from odoo.exceptions import UserError

SUPERUSER_ID = 2


class ModuleManagement(models.Model):
    _name = 'module.management'
    _description = 'Module Management'

    name = fields.Char(string='Name')
