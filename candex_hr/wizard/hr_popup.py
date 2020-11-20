# -*- coding: utf-8 -*-
from operator import itemgetter
from odoo import api, fields, models


class HrPopup(models.TransientModel):
    _name = 'hr.popup'

    user_ids = fields.Many2many('res.users', string='Next Hiring Managers')
    next_meeting_date = fields.Date('Next Meeting Date')
    survey_link = fields.Char('Survey Link')

    def action_move_state_confirm(self):
        applicant = self.env['hr.applicant'].browse(self.env.context.get('active_ids'))

        # get list stages
        hr_stage_action_ids = applicant.job_id.hr_stage_action_ids
        stage_dict = []
        stage_ids = []
        for hs in hr_stage_action_ids:
            stage_dict.append({
                'id'      : hs.hr_recruitment_stage_id.id,
                'sequence': hs.hr_recruitment_stage_id.sequence,
            })
        if stage_dict:
            stage_dict = sorted(stage_dict, key=itemgetter('sequence'), reverse=False)
            for st in stage_dict:
                stage_ids.append(st.get('id'))

        # get next stage_id
        current_stage_id = applicant.stage_id.id
        next_stage_id = stage_ids[stage_ids.index(current_stage_id) + 1]

        # write applicant
        if self.send_email(applicant):
            write_vals = {
                'stage_id': next_stage_id,
                'next_meeting_date': self.next_meeting_date,
                'user_ids': self.user_ids
            }
            applicant.write(write_vals)
            return True
        else:
            raise IOError("Can not send email!")

    def send_email(self, applicant):
        """
        :param applicant:
        :return:
        """
        if applicant and applicant.stage_id.id == 1:
            template_id = self.env.ref('candex_hr.email_template_hr_stage_screen')
        elif applicant and applicant.stage_id.id == 2:
            template_id = self.env.ref('candex_hr.email_template_hr_stage_first_interview').id
        template_id.send_mail(applicant.id, force_send=True)
        return True

