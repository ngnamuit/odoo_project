# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from math import copysign
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)
SUPERUSER_ID = 2

class ResGroup(models.Model):
    _inherit = 'res.groups'

    code = fields.Selection(
        [
            ('user', 'User'),
            ('admin', 'Admin'),
            ('support', 'Support'),
        ], string="Code", default='user')
