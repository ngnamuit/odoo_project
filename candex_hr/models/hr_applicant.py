import logging
import ast
from odoo import api, fields, models, registry, _
from odoo_project.candex_crm.models import utils as BaseUtils

_logger = logging.getLogger(__name__)


def get_facebook_config(self):
    icp    = self.env['ir.config_parameter'].sudo()
    config = str(icp.get_param("facebook_config", default={}))
    return ast.literal_eval(str(config))

class HrApplicant(models.Model):
    _inherit    = "hr.applicant"

    title_name = fields.Selection([
        ('anh', 'Anh'),
        ('chi', 'Chị'),
        ('mr', 'Mr'),
        ('ms', 'Ms')
    ], default="mr", string='Name Title')
    first_name = fields.Char(string='First Name', translate=True)
    last_name  = fields.Char(string='Last Name', translate=True)
    gender     = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others')
    ],  default="male", tracking=True)

    birthday   = fields.Date('Date of Birth', tracking=True)
    lang       = fields.Selection([
        ('vietnamese', 'Vietnamese'),
        ('english', 'English'),
        ('japanese', 'Japanese'),
        ('chinese', 'Chinese'),
        ('korean', 'Korean'),
        ('french', 'French'),
        ('others', 'Others')
    ], string='Language', validate=False)
    status = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('others', 'Others')
    ], string='Marital Status', tracking=True)
    function = fields.Selection(
    [
        ('accounting', 'Accounting | Finance | Investment'),
        ('customer', 'Customer'),
        ('service', 'Service'),
        ('sale', 'Sales | Business'),
        ('development', 'Development'),
        ('hr', 'HR | Recruitment | Training'),
        ('engineering', 'Engineering | R & D'),
        ('administration', 'Administration | Office'),
        ('support', 'Support'),
        ('information', 'Information'),
        ('technology', 'Technology'),
        ('marketing', 'Marketing | Media and Communication'),
        ('procurement', 'Procurement | Supply'),
        ('logistic', 'Chain | Logistic'),
        ('manufacturing', 'Production(Manufacturing)'),
        ('consulting', 'Consulting | Project'),
        ('management', 'Management'),
        ('others', 'Others')
    ], string='Job Function', tracking=True)
    industry = fields.Selection([
        ('sale', 'SALES / MARKETING'),
        ('service', 'SERVICES'),
        ('manufacturing', 'MANUFACTURING'),
        ('fmcg', 'FMCG'),
        ('computer', 'COMPUTER / IT'),
        ('admin_hr', 'ADMIN / HR'),
        ('accounting', 'ACCOUNTING / FINANCE'),
        ('communication_media', 'COMMUNICATION / MEDIA'),
        ('building_construction', ' BUILDING / CONSTRUCTION'),
        ('engineering', 'ENGINEERING'),
        ('education', 'EDUCATION / TRAINING'),
        ('healthcare', 'HEALTHCARE'),
        ('sciences', 'SCIENCES'),
        ('hospitality_tourism', 'HOSPITALITY / TOURISM'),
        ('others', 'Others')
    ], string='Industry', tracking=True)
    seniority = fields.Selection([
        ('student', 'Student'),
        ('intern', 'Intern'),
        ('entry_level', 'Entry Level'),
        ('senior_level', 'Senior Level(Non - Manager)'),
        ('manager', 'Manager'),
        ('head', 'Head of Department'),
        ('c_level', 'C - Level')
    ], string='Seniority', tracking=True)
    work_email = fields.Char("Email Working", tracking=True)
    name = fields.Char("Subject / Application Name", required=False)

    @api.model
    def create(self, vals):
        if 'first_name' in vals or 'last_name' in vals:
            vals.update({'name': f"{vals['first_name']} {vals['last_name']}"})
        res = super(HrApplicant, self).create(vals)
        return res