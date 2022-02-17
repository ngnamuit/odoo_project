# -*- coding: utf-8 -*-
import uuid

from collections import Counter, OrderedDict
from itertools import product
from werkzeug import urls
import random

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.exceptions import AccessError
FILETYPE_BASE64_MAGICWORD = {
    b'/': 'jpg',
    b'R': 'gif',
    b'i': 'png',
    b'P': 'svg+xml',
}

class Survey(models.Model):
    _inherit = 'survey.survey'

    company_id = fields.Many2one('res.company', compute='_compute_company')
    survey_done = fields.Html(
        'Survey Done', translate=True, sanitize=False,  # TDE TODO: sanitize but find a way to keep youtube iframe media stuff
        help="Use this field to add additional explanations about your question or to illustrate it with pictures or a video")

    pdf_footer = fields.Binary(string="PDF Footer")
    pdf_header = fields.Binary(string="PDF Header")

    def _compute_company(self):
        for record in self:
            record.company_id = record.env.user.company_id

    def image_data_uri(self, base64_source):
        """This returns data URL scheme according RFC 2397
        (https://tools.ietf.org/html/rfc2397) for all kind of supported images
        (PNG, GIF, JPG and SVG), defaulting on PNG type if not mimetype detected.
        """
        company = self.env['res.company'].sudo().browse(1)
        base64_source = company.logo
        return 'data:image/%s;base64,%s' % (
            FILETYPE_BASE64_MAGICWORD.get(base64_source[:1], 'png'),
            base64_source.decode(),
        )
    # def _get_next_page_or_question(self, user_input, page_or_question_id=False, go_back=False):
    #     if page_or_question_id is False:
    #         survey = user_input.survey_id
    #         pages_or_questions = survey._get_pages_or_questions(user_input)
    #         ids = pages_or_questions.ids
    #         page_or_question_id = ids[0]
    #         go_back = False
    #     return super(Survey, self)._get_next_page_or_question(user_input, page_or_question_id, go_back)

class SurveyQuestion(models.Model):
    _inherit = 'survey.question'
    question_type = fields.Selection(selection_add=[('currency', 'Currency'), ('percentage', 'Percentage')])

    def validate_question(self, answer, comment):
        if self.constr_mandatory and self.question_type in ['currency', 'percentage']:
            if answer:
                return {}
            else:
                return {self.id: self.constr_error_msg}
        return super(SurveyQuestion, self).validate_question(answer, comment)
