# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class ProjectInherirt(models.Model):
    _inherit = "project.project"
    _description = "Project"

    note = fields.Char("Note")
    remark = fields.Char("Remark")
    kind_of_dossier_id = fields.Many2one("kind.of.dossier", string="Kind of Dossier")
    kind_of_variation_id = fields.Many2one("kind.of.variation", string="Sub Dossiers")
    exp_date = fields.Date("Exp.Date FSC/CPP")
    test_result = fields.Datetime("Test Result")
    product_template_id = fields.Many2one("product.template", string="Product")
    application_line_id = fields.Many2one("application.line", string="Application")
    manufactory_line_id = fields.Many2one("manufactory.line", string="Manufacturer")
    res_partner_id = fields.Many2one("res.partner", string="Customer")
    info_lines = fields.One2many("project.info.line", "project_id", string="Project Task")
