import logging
import ast
from odoo import api, fields, models, registry, _
from odoo_project.candex_crm.models import utils as BaseUtils

_logger = logging.getLogger(__name__)


class RejectReason(models.Model):
    _name = "reject.reason"

    name = fields.Char('Name')


class HrStateAction(models.Model):
    _name = "hr.state.action"

    name = fields.Char('Name')
    sequence = fields.Integer("Sequence", default=10, help="Gives the sequence order when displaying a list of stages.")
    hr_recruitment_stage_id = fields.Many2one('hr.recruitment.stage', string='State', required=True)
    user_ids = fields.Many2many('res.users', string='Hiring Managers')


class HrJob(models.Model):
    _inherit    = "hr.job"

    hr_stage_action_ids = fields.Many2many(
        'hr.state.action', 'hr_job_state_action',
        'hr_job_id', 'hr_state_action_id',
        string='State Actions')
    survey_id = fields.Many2one('survey.survey', string='Survey')
    reject_reason_ids = fields.Many2many(
        'reject.reason', 'hr_job_reject_reason',
        'hr_job_id', 'reject_reason_id',
        string='Reject Reasons')


class RecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    reminder_days = fields.Integer('Reminder Days (Int)', default=0)
    need_to_do_survey = fields.Boolean('Need to do survey')
