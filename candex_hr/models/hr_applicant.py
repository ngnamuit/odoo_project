import logging
import ast
from datetime import datetime, date
from dateutil import relativedelta
from odoo import api, fields, models, registry, _
from odoo_project.candex_crm.models import utils as BaseUtils
from odoo.addons.base.models.ir_ui_view import keep_query

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
    user_ids = fields.Many2many('res.users', string='Hiring Managers')
    next_meeting_date = fields.Date('Next Meeting Date')
    is_sent_email = fields.Boolean('Is Sent Email?')
    survey_id = fields.Many2one('survey.survey')


    @api.model
    def create(self, vals):
        if 'first_name' in vals or 'last_name' in vals:
            vals.update({'name': f"{vals['first_name']} {vals['last_name']}"})
        res = super(HrApplicant, self).create(vals)
        return res


    def action_move_new_stage(self):
        """
        Opens a wizard to compose an email, with relevant mail template loaded by default
        """
        self.ensure_one()
        popup_action = self.env.ref('candex_hr.hr_popup_move_state_view_action')
        dict_act_window = popup_action.read([])[0]
        tomorrow = datetime.today().date() + relativedelta.relativedelta(days=1)
        survey_link = self.get_survey_link()
        user_ids = []
        for hr in self.job_id.hr_stage_action_ids:
            if hr.hr_recruitment_stage_id == self.stage_id:
                user_ids=hr.user_ids.ids
        if self.stage_id and self.stage_id.need_to_do_survey:
            dict_act_window['context'] = {
                'default_survey_link': survey_link,
                'default_next_meeting_date': tomorrow,
                'default_user_ids': user_ids,
            }
        else:
            dict_act_window['context'] = {
                'default_next_meeting_date': tomorrow
            }
        return dict_act_window


    def _fetch_from_access_token(self, survey_token, answer_token):
        """ Check that given token matches an answer from the given survey_id.
        Returns a sudo-ed browse record of survey in order to avoid access rights
        issues now that access is granted through token. """
        survey_sudo = self.env['survey.survey'].with_context(active_test=False).sudo().search([('access_token', '=', survey_token)])
        if not answer_token:
            answer_sudo = self.env['survey.user_input'].sudo()
        else:
            answer_sudo = self.env['survey.user_input'].sudo().search([
                ('survey_id', '=', survey_sudo.id),
                ('token', '=', answer_token)
            ], limit=1)
        return survey_sudo, answer_sudo

    def get_survey_link(self):
        survey = self.job_id.survey_id
        if survey:
            survey_sudo, dummy = self._fetch_from_access_token(survey.access_token, False)
            answer_sudo = survey_sudo._create_answer(user=self.env.user, test_entry=True)
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            url = f'{base_url}/survey/start/%s?%s' % (survey_sudo.access_token, keep_query('*', answer_token=answer_sudo.token))
            return url
        else:
            raise IOError("Can not send email!")