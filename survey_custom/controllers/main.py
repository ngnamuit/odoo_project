# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
import werkzeug

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import fields, http, _
from odoo.addons.base.models.ir_ui_view import keep_query
from odoo.addons.survey.controllers.main import Survey
from odoo.exceptions import UserError
from odoo.http import request, content_disposition
from odoo.osv import expression
from odoo.tools import format_datetime, format_date, is_html_empty

from odoo.addons.web.controllers.main import Binary

_logger = logging.getLogger(__name__)

# 
class SurveyCustom(Survey):

    @http.route('/survey/submit_on_print/<string:survey_token>/<string:answer_token>', type='http', auth='public', website=True)
    def survey_submit_on_print(self, survey_token, answer_token=None, **post):
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=False)
        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        if answer_sudo.state == 'review' and answer_sudo.test_entry is True and answer_sudo.note == 'Answer is reviewing':
            answer_sudo.write({'test_entry': False, 'state': 'done'})

        return request.render('survey.survey_fill_form_done', {
            'survey': survey_sudo,
            'answer': answer_sudo if survey_sudo.scoring_type != 'scoring_without_answers' else answer_sudo.browse()
        })

    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>', type='json', auth='public', website=True)
    def survey_submit(self, survey_token, answer_token, **post):
        res = super(SurveyCustom, self).survey_submit(survey_token, answer_token, **post)
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        _, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        if answer_sudo.state == 'done':
            if answer_sudo.test_entry is False:
                answer_sudo.write({
                    'test_entry': True,
                    'note': 'Answer is reviewing',
                    'state': 'review'
                })
        return res

    @http.route('/survey/retry/<string:survey_token>/<string:answer_token>', type='http', auth='public', website=True)
    def survey_retry(self, survey_token, answer_token, **post):
        user_input = request.env['survey.user_input'].sudo().search([('access_token', '=', answer_token)], limit=1)
        print("user_input.state == == " + str(user_input.state))
        if user_input and user_input.state == 'review':
            user_input.write({'state': 'in_progress'})

            # region get previous_page_id
            survey = user_input.survey_id
            pages_or_questions = survey._get_pages_or_questions(user_input)
            ids = pages_or_questions.ids
            previous_page_id = ids[0]
            # endregion

            res = self.survey_display_page(survey_token, answer_token, **{'previous_page_id': previous_page_id})
        else:
            res = super(SurveyCustom, self).survey_submit(survey_token, answer_token, **post)
        return res