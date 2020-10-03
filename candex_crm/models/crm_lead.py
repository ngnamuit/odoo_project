import logging
import ast
from odoo import api, fields, models, registry, _
from . import utils as BaseUtils

_logger = logging.getLogger(__name__)

LIFECYCLE_STAGE = [
    ('subscriber', 'Subscriber'),
    ('lead', 'Lead'),
    ('candidate', 'Candidate'),
    ('employee', 'Employee'),
    ('alumni', 'Alumni')
]


def get_lifecycle_stage(self):
    icp = self.env['ir.config_parameter'].sudo()
    lst = icp.get_param("LIFECYCLE_STAGE", default=[])
    if lst:
        lst = ast.literal_eval(lst)
        return lst
    else:
        return LIFECYCLE_STAGE


class CrmLead(models.Model):
    _name = "crm.lead.activities"

    platform     = fields.Char(string='Platform')
    source       = fields.Char(string='Source')
    content      = fields.Text(string='Content')
    type         = fields.Selection(LIFECYCLE_STAGE, string='Activity Type')
    contact_id   = fields.Many2one('res.partner', string="Contact ID")
    lead_id      = fields.Many2one('crm.lead', string="Lead ID")



class CrmLead(models.Model):
    _inherit    = "crm.lead"

    lead_activities    = fields.One2many('crm.lead.activities', 'lead_id')
    contact_id         = fields.Many2one('res.partner', string='Contact')

    title_name   = fields.Selection(BaseUtils.get_name_title, string='Name Title')
    first_name   = fields.Char(string='First Name', translate=True)
    last_name    = fields.Char(string='Last Name', translate=True)
    email        = fields.Char(string='Email')
    function     = fields.Char(string='Job Position')
    title        = fields.Many2one('res.partner.title', string='Job Title')
    company_name = fields.Char(string='Company Name')
    company_id   = fields.Many2one('res.company', 'Company',
                                   default=lambda self: self.env.company,
                                   index=True, required=True)


    lifecycle_stage = fields.Selection(get_lifecycle_stage, string='Lifecycle Stage', default='lead')
    last_contacted  = fields.Datetime(string='Last Contacted', readonly=True,
                                      help="The last time a call, sales email, or meeting was logged for this Vacancy."
                                            " This is set automatically by system based on user actions")
    history_ids = fields.One2many(
        'mail.message', 'res_id', string='Messages',
        domain=lambda self: [('message_type', '!=', 'user_notification')], auto_join=True)

    def _compute_name(self):
        for crm in self:
            crm.name = '{} {}'.format(crm.first_name or '', crm.last_name or '')
