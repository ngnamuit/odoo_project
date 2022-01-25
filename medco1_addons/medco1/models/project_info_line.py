# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

class ProjectInfoLine(models.Model):
    _name = "project.info.line"
    _description = "Project Info Line"

    project_id = fields.Many2one("project.project",  string="Project Id")
    emp_medco_hcm_id = fields.Many2one("hr.employee", string="Employee MedCo HCM",
                                       domain=[('department_id.name', '=', 'MedCo HCM')])
    emp_medco_hn_id = fields.Many2one("hr.employee", string="Employee MedCo HN",
                                      domain=[('department_id.name', '=', 'MedCo HN')])
    emp_expert_id = fields.Many2one("hr.employee", string="Medical Expert",
                                    domain=[('department_id.name', '=', 'Cục quản lý Dược')])



