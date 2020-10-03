import logging
from odoo import api, fields, models, registry, _
from odoo_project.candex_crm.models import utils as BaseUtils


_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _name    = "res.partner"
    _inherit = ['res.partner', 'mail.thread']

    name         = fields.Char(string='Full Name', compute='_compute_name', translate=True)
    first_name   = fields.Char(string='First Name', translate=True)
    last_name    = fields.Char(string='Last Name', translate=True)
    title_name   = fields.Selection(BaseUtils.get_name_title, string='Name Title', default="mr")

    last_contacted  = fields.Datetime(string='Last Contacted', readonly=True,
                                      help="The last time a call, sales email, or meeting was logged for this Vacancy."
                                            " This is set automatically by system based on user actions")

    def _compute_name(self):
        for partner in self:
            partner.name = '{} {}'.format(partner.first_name or '', partner.last_name or '')