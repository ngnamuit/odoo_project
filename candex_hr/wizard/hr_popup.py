# -*- coding: utf-8 -*-
from operator import itemgetter
from odoo import api, fields, models


class HrPopup(models.TransientModel):
    _name = 'hr.popup'

    user_ids = fields.Many2many('res.users', string='Next Hiring Managers')
    next_meeting_date = fields.Datetime('Next Meeting Date')
    survey_link = fields.Char('Survey Link')

    def action_move_state_confirm(self):
        self.ensure_one()
        applicant = self.env['hr.applicant'].browse(self.env.context.get('active_ids'))

        # write applicant
        sent = True
        if sent:
            write_vals = {
                'stage_id': applicant.get_next_state(),
                'next_meeting_date': self.next_meeting_date,
                'user_ids': self.user_ids
            }
            applicant.write(write_vals)
            self.send_email_to_confirm(applicant)
            return True
        else:
            raise IOError("Can not send email!")

    def send_email_to_confirm(self, applicant):
        self.ensure_one()
        applicant.ensure_one()
        template_id = applicant.stage_id.template_id
        if template_id:
            template_id.send_mail(applicant.id)
        return True

    def get_interview_submit_link(self, applicant):
        url_yes = f'/applicant/interview/submit/say_yes/{applicant.stage_id.id}/{applicant.token}'
        url_no = f'/applicant/interview/submit/say_no/{applicant.stage_id.id}/{applicant.token}'
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        return f'{base_url}{url_yes}', f'{base_url}{url_no}'
