# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class ManufactoryLine(models.Model):
    _name = "manufactory.line"
    _description = "Manufactory Lines"

    code = fields.Char("Code")
    name = fields.Char("Name")
    note = fields.Char("Note")
    res_partner_id = fields.Many2one("res.partner", string="Customer")
    application_line_id = fields.Many2one("application.line", string="Application")



