# -*- coding: utf-8 -*-
import uuid

from collections import Counter, OrderedDict
from itertools import product
from werkzeug import urls
import random

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression


class Survey(models.Model):
    _inherit = 'survey.survey'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)

    def action_start_survey(self):
        """ Open the website page with the survey form """
        super(Survey, self).action_start_survey()
        company_domain = self.env.user.company_id.domain
        public_url = f'https://{company_domain}/'
        token = self.env.context.get('survey_token')
        trail = "?answer_token=%s" % token if token else ""
        return {
            'type': 'ir.actions.act_url',
            'name': "Start Survey",
            'target': 'self',
            'url': public_url + trail
        }

class SlideChannel(models.Model):
    _inherit = 'slide.channel'

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)

class SlideSlide(models.Model):
    _inherit = 'slide.slide'

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)


class SlideQuestion(models.Model):
    _inherit = 'slide.question'

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)

class SlideQuestion(models.Model):
    _inherit = 'slide.tag'

    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                     default=lambda self: self.env.company)
