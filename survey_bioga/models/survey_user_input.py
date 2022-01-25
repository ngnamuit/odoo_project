# -*- coding: utf-8 -*-
from odoo import fields, api, models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    def save_lines(self, question, answer, comment=None):
        old_answers = self.env['survey.user_input.line'].search([
            ('user_input_id', '=', self.id),
            ('question_id', '=', question.id)
        ])
        if question.question_type in ['currency', 'percentage']:
            self._save_line_simple_answer(question, old_answers, answer, comment)
        else:
            return super(SurveyUserInput, self).save_lines(question, answer, comment)

    def _save_line_simple_answer(self, question, old_answers, answers, comment=None):
        vals = {
            'user_input_id': self.id,
            'question_id': question.id,
            'skipped': False,
            'answer_type': 'char_box',
            'value_char_box': answers

        }
        if answers and old_answers:
            return old_answers.write(vals)
        elif not answers and old_answers:
            vals.update({'answer_type': None, 'skipped': True})
        else:
            return self.env['survey.user_input.line'].create(vals)

    def _mark_done(self):
        res = super(SurveyUserInput, self)._mark_done()

        for user_input in self:
            index = 0
            project_name = ''
            full_name = ''
            email = ''
            for line in user_input.user_input_line_ids:
                index +=1
                if index == 1: # question 1
                    project_name = line.value_char_box or line.value_text_box or ''
                if index == 3: # question 3
                    full_name = line.value_char_box or line.value_text_box or ''
                if index == 4: # question 4
                    email = line.value_char_box or line.value_text_box or ''
            # send email
            template = self.env.ref('survey_custom.mail_template_survey_submitted_en')
            survey_id = user_input.survey_id.id
            ctx = {
                'project_name': project_name,
                'full_name': full_name,
                'email': email
            }
            template.sudo().with_context(ctx).send_mail(survey_id, force_send=True)
        return res