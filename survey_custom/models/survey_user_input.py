# -*- coding: utf-8 -*-
from odoo import fields, api, models, SUPERUSER_ID
import base64
import copy


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    note = fields.Char(string='Note')
    state = fields.Selection([
        ('new', 'Not started yet'),
        ('in_progress', 'In Progress'),
        ('review', 'In Review'),
        ('done', 'Completed'),
    ], string='Status', default='new', readonly=True)

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
        return res

    def send_submitted_survey_email(self):
        self = self.with_user(SUPERUSER_ID)
        for user_input in self:
            if user_input.survey_id and user_input.state in ['review', 'done']:
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

                # generate pdf file
                survey_sudo = user_input.survey_id
                answer_sudo = user_input
                data = {
                    'project_name': project_name.upper(),
                    'survey': survey_sudo,
                    'answer': answer_sudo,
                    'questions_to_display': user_input._get_print_questions(),
                    'scoring_display_correction': survey_sudo.scoring_type == 'scoring_with_answers' and answer_sudo,
                }
                pre_data = user_input.prepare_data_to_render_pdf()
                report_template_id = self.env.ref(
                    'survey_custom.action_submitted_survey_pdf_report')._render_qweb_pdf(user_input.id, data=pre_data)
                data_record = base64.b64encode(report_template_id[0])
                ir_values = {
                    'name': "%s - Submitted at ITI FUND.pdf"%(project_name),
                    'type': 'binary',
                    'datas': data_record,
                    'store_fname': data_record,
                    'mimetype': 'application/x-pdf',
                }
                data_id = self.env['ir.attachment'].create(ir_values)

                # send email
                template = self.env.ref('survey_custom.mail_template_survey_submitted_en')
                template.attachment_ids = [(6, 0, [data_id.id])]   # attach pdf into email
                survey_id = user_input.survey_id.id
                ctx = {
                    'project_name': project_name,
                    'full_name': full_name,
                    'email': email
                }
                template.sudo().with_context(ctx).send_mail(survey_id, force_send=True)
        return True

    def action_report_pdf(self):
        data = self.prepare_data_to_render_pdf()
        return self.env.ref('survey_custom.action_submitted_survey_pdf_report').report_action([], data=data)


    def prepare_data_to_render_pdf(self):
        user_input = self
        index = 0
        for line in user_input.user_input_line_ids:
            index +=1
            if index == 1: # question 1
                project_name = line.value_char_box or line.value_text_box or ''
        survey_sudo = user_input.survey_id
        question_and_page_ids = survey_sudo.question_and_page_ids
        answer_sudo = user_input
        user_input_line_ids = answer_sudo.user_input_line_ids

        # to dict
        survey_dict = survey_sudo.read(list(set(self.env['survey.survey']._fields)))
        question_and_page_dict = question_and_page_ids.read(list(set(self.env['survey.question']._fields)))
        answer_model_sudo = self.env['survey.question.answer'].sudo()

        for question in question_and_page_dict:
            if question['question_type'] in ['simple_choice', 'multiple_choice']:
                if 'suggested_answer_ids' in question:
                    suggested_answer_ids = copy.deepcopy(question.get('suggested_answer_ids', []))
                    if suggested_answer_ids:
                        suggested_answer_dict = []
                        for answer in answer_model_sudo.search([('id', 'in', suggested_answer_ids)]):
                            suggested_answer_dict.append({
                                'is_correct': answer.is_correct,
                                'id': answer.id,
                                'answer_score': answer.answer_score,
                                'value': answer.value
                            })
                        question['suggested_answer_ids'] = suggested_answer_dict

        answer_dict = answer_sudo.read(list(set(self.env['survey.user_input']._fields)))
        user_input_lines_dict = user_input_line_ids.read(list(set(self.env['survey.user_input.line']._fields)))
        question_ids = []
        line_index = 0
        for line in user_input_lines_dict:
            # upper question 1
            line_index += 1
            if line_index == 1:
                value_char_box = line['value_char_box'].upper()
                line['value_char_box'] = value_char_box
            files = []
            if line.get('user_binary_line'):
                for file in self.env['survey.binary'].search([('id', 'in', line['user_binary_line'])]):
                    files.append({
                        'id': file.id,
                        'binary_data': file.binary_data,
                        'binary_filename': file.binary_filename,
                    })
                line['user_binary_line'] = files
            is_render_question = False
            if line['question_id'] in question_ids:
                is_render_question = True
            question_ids.append(line['question_id'])
            line['is_render_question'] = is_render_question
        data = {
            'project_name': project_name.upper(),
            'survey': survey_dict,
            'question_and_page_ids': question_and_page_dict,
            'answer': answer_dict,
            'user_input_lines_dict': user_input_lines_dict,
            'questions_to_display': user_input._get_print_questions(),
            'scoring_display_correction': survey_sudo.scoring_type == 'scoring_with_answers' and answer_sudo,
        }
        return data