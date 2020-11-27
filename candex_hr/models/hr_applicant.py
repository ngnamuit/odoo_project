import ast
import logging
import werkzeug
import json
import uuid
from dateutil import relativedelta
from datetime import datetime
from operator import itemgetter
from odoo import api, fields, models, registry, _, http
from odoo.addons.base.models.ir_ui_view import keep_query
from odoo.http import request, content_disposition
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# contants
APPLICANT_ACTIVITY_TYPES = ['survey', 'submit_next_meeting_date']


class HrApplicantController(http.Controller):

    @http.route('/applicant/interview/submit/say_yes/<int:stage_id>/<string:applicant_token>', type='http', auth='user', website=True)
    def interview_submit_yes(self, stage_id, applicant_token, **kwargs):
        """
        This link is sent to customer to confirm that He/She agrees for next interview
        """
        applicant_id = request.env['hr.applicant'].sudo().search([
            ('token', '=', applicant_token.strip()),
            ('is_confirm_meeting', '=', False)
        ], limit=1)
        if not applicant_id or (applicant_id and applicant_id.stage_id.id != stage_id):
            return json.dumps({'error_message': "The applicant is invalid"})
        try:
            act_id = request.env['hr.applicant.activities'].sudo().create({
                'link': f'/applicant/interview/submit/say_yes/{stage_id}/{applicant_token}',
                'note': f'Say Yes - From State:{applicant_id.stage_id.name}',
                'type': 'submit_next_meeting_date',
                'stage_id': applicant_id.stage_id.id,
            })
            applicant_id.write({
                'applicant_activity_ids': [(6,0, [act_id.id])],
                'is_confirm_meeting': True
            })
            template_id = request.env.ref('candex_hr.email_template_user_confirm_interview')
            template_id.with_context(
                subject=f'Applicant of {applicant_id.get_full_name()} - Say Yes',
                email_from=applicant_id.department_id.company_id.email,
                email_to=applicant_id.job_id.user_id.email or 'test@gmail.com'
            ).send_mail(applicant_id.id,
                         force_send=True,
                         email_values={
                             'body': f'<p>User: {applicant_id.get_full_name()} - Confirm yes to go next meeting</p>'
                         })
        except Exception as error:
            return json.dumps({'error_message': str(error)})
        return json.dumps({'is_success': 200})

    @http.route('/applicant/interview/submit/say_no/<int:stage_id>/<string:applicant_token>', type='http', auth='user', website=True)
    def interview_submit_no(self, stage_id, applicant_token, **kwargs):
        """
        This link is sent to customer to confirm that He/She agrees for next interview
        """
        applicant_id = request.env['hr.applicant'].sudo().search([
            ('token', '=', applicant_token),
            ('is_confirm_meeting', '=', False)
        ], limit=1)
        if not applicant_id or (applicant_id and applicant_id.stage_id.id != stage_id):
            return json.dumps({'error_message': "The applicant is invalid"})
        try:
            act_id = request.env['hr.applicant.activities'].sudo().create({
                'link': f'/applicant/interview/submit/say_yes/{stage_id}/{applicant_token}',
                'note': f'Say No - From State : {applicant_id.stage_id.name}',
                'type': 'submit_next_meeting_date',
                'stage_id': applicant_id.stage_id.id,
            })
            applicant_id.write({
                'applicant_activity_ids': [(6, 0, [act_id.id])],
                'is_confirm_meeting': True,
                'stage_id': 5 # state reject
            })
            template_id = request.env.ref('candex_hr.email_template_user_confirm_interview')
            template_id.with_context(
                subject=f'Applicant of {applicant_id.get_full_name()} - Rejected by him/her',
                email_from=applicant_id.department_id.company_id.email,
                email_to=applicant_id.job_id.user_id.email or 'test@gmail.com'
            ).send_mail(applicant_id.id,
                         force_send=True,
                         email_values={
                             'body': f'<p>User: {applicant_id.get_full_name()} - Reject this applicant </p>'
                         })

        except Exception as error:
            return json.dumps({'error_message': str(error)})
        return json.dumps({'is_success': 200})

class HrApplicant(models.Model):
    _inherit    = "hr.applicant"

    is_confirm_meeting = fields.Boolean('Is Confirm Next Meeting Date',)
    token = fields.Char('Applicant Token')
    applicant_activity_ids = fields.One2many('hr.applicant.activities', 'applicant_id', string='Activities')
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
    next_meeting_date = fields.Datetime('Next Meeting Date')
    is_sent_email = fields.Boolean('Is Sent Email?')
    survey_id = fields.Many2one('survey.survey')
    job_stage_ids = fields.Many2many('hr.recruitment.stage', compute='_compute_job_stage_ids', string='Computed Stage')
    url_confirm_yes = fields.Char(string='URL to confirm Yes', compute='_compute_url_confirm_yes')
    url_confirm_no = fields.Char(string='URL to Reject', compute='_compute_url_confirm_no')

    @api.depends('job_id')
    def _compute_job_stage_ids(self):
        for applicant in self:
            stage_ids = []
            if applicant.job_id and applicant.job_id.hr_stage_action_ids:
                stage_ids = applicant.job_id.hr_stage_action_ids.hr_recruitment_stage_id.ids
            applicant.job_stage_ids = stage_ids

    @api.depends('stage_id')
    def _compute_url_confirm_yes(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        for applicant in self:
            url = f'{base_url}/applicant/interview/submit/say_yes/{applicant.stage_id.id}/{applicant.token}'
            applicant.url_confirm_yes = url

    @api.depends('stage_id')
    def _compute_url_confirm_no(self):
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        for applicant in self:
            url = f'{base_url}/applicant/interview/submit/say_no/{applicant.stage_id.id}/{applicant.token}'
            applicant.url_confirm_no = url

    @api.model
    def get_full_name(self):
        return f'{self.first_name or ""} {self.last_name or ""}'

    @api.model
    def create(self, vals):
        if 'first_name' in vals or 'last_name' in vals:
            vals.update({'name': f"{vals['first_name']} {vals['last_name']}"})
        if 'job_id' in vals and vals['job_id']:
            first_stage_id = self.get_first_stage_by_job_id(vals['job_id'])
            user_ids       = self.get_user_ids_by_job_id(vals['job_id'], first_stage_id)
            vals['stage_id'] = first_stage_id
            vals['user_ids'] = user_ids
        vals['token'] = uuid.uuid4()
        res = super(HrApplicant, self).create(vals)
        return res

    def write(self, vals):
        if 'stage_id' in vals and 'is_confirm_meeting' not in vals:
            vals['is_confirm_meeting'] = False
            if not self.token:
                vals['token'] = uuid.uuid4()
        return super(HrApplicant, self).write(vals)


    def get_user_ids_by_job_id(self, job_id, current_state_id):
        job = self.env['hr.job'].browse(job_id)
        user_ids = []
        for hs in job.hr_stage_action_ids:
            if hs.hr_recruitment_stage_id.id == current_state_id:
                user_ids =hs.user_ids.ids
        return user_ids

    def get_first_stage_by_job_id(self, job_id):
        job = self.env['hr.job'].browse(job_id)
        if not job or (job and not job.hr_stage_action_ids):
            return None
        # get list stages
        hr_stage_action_ids = job.hr_stage_action_ids
        stage_dict = []
        stage_ids = []
        for hs in hr_stage_action_ids:
            stage_dict.append({
                'id': hs.hr_recruitment_stage_id.id,
                'sequence': hs.hr_recruitment_stage_id.sequence,
            })
        if stage_dict:
            stage_dict = sorted(stage_dict, key=itemgetter('sequence'), reverse=False)
            for st in stage_dict:
                stage_ids.append(st.get('id'))

        # get next stage_id
        try:
            current_stage_id = stage_ids[0]
            return current_stage_id
        except:
            return None

    def get_next_state(self):
        """
        :return:
        - next state if applicant has job_id that it defined hr_stage_action_ids
        - None: for case that not job_id or not hr_stage_action_ids or that is last state of job_id
        """
        if not self.job_id or (self.job_id and not self.job_id.hr_stage_action_ids):
            return None
        # get list stages
        hr_stage_action_ids = self.job_id.hr_stage_action_ids
        stage_dict = []
        stage_ids = []
        for hs in hr_stage_action_ids:
            stage_dict.append({
                'id': hs.hr_recruitment_stage_id.id,
                'sequence': hs.hr_recruitment_stage_id.sequence,
            })
        if stage_dict:
            stage_dict = sorted(stage_dict, key=itemgetter('sequence'), reverse=False)
            for st in stage_dict:
                stage_ids.append(st.get('id'))

        # get next stage_id
        current_stage_id = self.stage_id.id
        try:
            next_stage_id = stage_ids[stage_ids.index(current_stage_id) + 1]
            return next_stage_id
        except:
            return None

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
        next_state_id = self.get_next_state()
        for hr in self.job_id.hr_stage_action_ids:
            if hr.hr_recruitment_stage_id.id == next_state_id:
                user_ids=hr.user_ids.ids
        context = {'default_next_meeting_date': tomorrow}
        if self.stage_id:
            context.update({
                'default_user_ids': user_ids,
            })
        if self.stage_id.need_to_do_survey:
            context.update({
                'default_survey_link': survey_link,
            })
        dict_act_window['context'] = context
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
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.response_id:
            response = self.survey_id._create_answer(partner=self.partner_id)
            self.response_id = response.id
        else:
            response = self.response_id

        token = response.token
        trail = "?answer_token=%s" % token if token else ""
        url  =  str(self.survey_id.public_url + trail)
        return url

    # def get_survey_link(self):
    #     survey = self.job_id.survey_id
    #     if survey:
    #         survey_sudo, dummy = self._fetch_from_access_token(survey.access_token, False)
    #         answer_sudo = survey_sudo._create_answer(user=self.env.user, test_entry=True)
    #         base_url = self.env['ir.config_parameter'].get_param('web.base.url')
    #         url = f'{base_url}/survey/start/%s?%s' % (survey_sudo.access_token, keep_query('*', answer_token=answer_sudo.token))
    #         return url
    #     else:
    #         raise IOError("Can not send email!")

class HrApplicantActivities(models.Model):
    _name    = "hr.applicant.activities"

    applicant_id = fields.Many2one('hr.applicant')
    survey_id    = fields.Many2one('survey.survey', string='Survey')
    result_id    = fields.Many2one('survey.user_input', string='User Result')
    type         = fields.Char('Activity Type')
    user_id      = fields.Many2one('res.users', string='User')
    note         = fields.Text('Note')
    link         = fields.Char('Link')
    stage_id     = fields.Many2one('hr.recruitment.stage', string='State', required=True)

class SurveyUserInput(models.Model):

    _inherit = "survey.user_input"

    def write(self, vals):
        for rec in self:
            applicant_id = self.env['hr.applicant'].sudo().search([('response_id', '=', rec.id)], limit=1)
            if applicant_id and vals.get('state') == 'done':
                act_id = request.env['hr.applicant.activities'].sudo().create({
                    'survey_id': applicant_id.survey_id.id,
                    'result_id': rec.id,
                    'type': 'survey',
                    'stage_id': applicant_id.stage_id.id,
                })
                applicant_id.write({
                    'applicant_activity_ids': [(6, 0, [act_id.id])],
                })
        return super(SurveyUserInput, self).write(vals)