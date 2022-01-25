# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class ApplicationLine(models.Model):
    _name = "application.line"
    _description = "Application Lines"

    code = fields.Char("Code")
    name = fields.Char("Name")
    res_partner_id = fields.Many2one("res.partner", string="Res Partner Id")
    manufactory_lines = fields.One2many("manufactory.line", "application_line_id", string="Manufactory lines")

