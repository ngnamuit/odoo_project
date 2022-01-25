# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class KindOfVariation(models.Model):
    _name = "kind.of.variation"
    _description = "Sub Dossiers"

    code = fields.Char("Code")
    name = fields.Char("Name")
    qty_days = fields.Integer("Qty Days")
    kind_of_dossier_id = fields.Many2one("kind.of.dossier", string="Sub Dossiers")
