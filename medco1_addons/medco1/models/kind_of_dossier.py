# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class KindOfDossier(models.Model):
    _name = "kind.of.dossier"
    _description = "Sub Dossiers"

    code = fields.Char("Code")
    name = fields.Char("Name")
    sort_order = fields.Integer("Sort Order")
