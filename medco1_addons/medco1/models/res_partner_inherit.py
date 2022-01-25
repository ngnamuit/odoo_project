# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class ResParnterInherirt(models.Model):
    _inherit = "res.partner"
    _description = "Res Partner"

    manufactory_lines = fields.One2many("manufactory.line", "res_partner_id", string="Res Partner Id")
    application_lines = fields.One2many("application.line", "res_partner_id", string="Res Partner Id")


