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
        ('mr', 'Mr.'),
        ('ms', 'Ms.')
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
    job_title = fields.Selection([
        ('cccountant', 'Accountant'),
        ('customer_service_executive', 'Customer Service Executive'),
        ('business_development_manager', 'Business Development Manager'),
        ('line_technician', 'Line Technician'),
        ('receptionlist', 'Receptionlist'),
        ('java_developer', 'Java Developer'),
        ('product_manager', 'Product Manager'),
        ('purchaser', 'Purchaser'),
        ('line_manager', 'Line Manager'),
        ('project_manager', 'Project Manager'),
        ('training_assistant_manager', 'Training Assistant Manager'),
        ('recruiter', 'Recruiter'),
        ('brand_manager', 'Brand Manager'),
        ('marketing_executive', 'Marketing Executive'),
        ('designer', 'Designer'),
        ('warehouse_supervisor', 'Warehouse Supervisor'),
        ('hr_intern', 'HR Intern'),
        ('hr_manager', 'HR Manager'),
        ('marketing_director', 'Marketing Director'),
        ('head_production', 'Head of Production'),
        ('head_sales', 'Head of Sales'),
        ('art_director', 'Art Director'),
        ('accountant_manager', 'Accountant Manager'),
        ('coo', 'COO'),
        ('others', 'Others')
    ], string="Job Title")
    function = fields.Selection(
    [
        ('accounting', 'Accounting | Finance | Investment'),
        ('cs', 'Customer Service'),
        ('sale_bd', 'Sales | Business Development'),
        ('hr', 'HR | Recruitment | Training'),
        ('engineering', 'Engineering | R&D'),
        ('administration_support', 'Administration | Office Support'),
        ('it', 'Information Technology'),
        ('marketing', 'Marketing | Media and Communication'),
        ('procurement_logistic', 'Procurement | Supply Chain | Logistic'),
        ('manufacturing', 'Production (Manufacturing)'),
        ('consulting', 'Consulting | Project Management'),
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
        ('building_construction', 'BUILDING / CONSTRUCTION'),
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
        ('senior_level', 'Senior Level (Non-Manager)'),
        ('manager', 'Manager'),
        ('head', 'Head of Department'),
        ('c_level', 'C - Level')
    ], string='Seniority', tracking=True)
    work_email  = fields.Char("Email Working", tracking=True)
    name        = fields.Char("Subject / Application Name", required=False)
    history_ids = fields.One2many(
        'mail.message', 'res_id', string='Messages',
        domain=lambda self: [('message_type', '!=', 'user_notification')], auto_join=True)

    @api.model
    def create(self, vals):
        if 'first_name' in vals or 'last_name' in vals:
            vals.update({'name': f"{vals['first_name']} {vals['last_name']}"})
        res = super(HrApplicant, self).create(vals)
        return res