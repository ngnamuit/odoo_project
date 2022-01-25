# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from math import copysign
from odoo.exceptions import UserError
from odoo.addons.module_management.models.res_company import find_user_system_ids
_logger = logging.getLogger(__name__)
SUPERUSER_ID = 2


class ResCompanyType(models.Model):
    _name = 'res.company.type'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')
    group_id = fields.Many2one('res.groups', string='Management Group')
    group_ids = fields.Many2many('res.groups', string='Groups')
    default_categ_id = fields.Many2one('ir.module.category', string='Filter Category Id', default=lambda self: self._default_group_id())
    company_ids = fields.One2many('res.company', 'type_id', string='Companies')

    def _default_group_id(self):
        categ_id = self.env.ref('module_management.module_management_hidden')
        return categ_id.id

    def onchange_company_ids(self):
        group_id = self.group_id
        company_ids = self.company_ids.ids
        _logger.info(f"ACTION CHANGE COMPANY_IDS:")
        if group_id and group_id.users:
            for user in group_id.users:
                if user.id not in [1,2]:
                    company_ids += [user.company_id.id]
                    user.company_ids = [(5,0,0), (6, 0, company_ids)]
                    _logger.info(f"ACTION ADD COMPANY_IDS TO USER: user={user}, company_ids={company_ids}")

    @api.model
    def create(self, values):
        res = super(ResCompanyType, self).create(values)
        if values.get('group_id') and res.group_id:
            res.process_group_id(res.group_id)
        return res

    def write(self, values):
        """
        :group_id -> support group
        :group_ids -> groups that belong BT
        We have 3 main cases to add:
        # CASE 1: ACTION CHANGE FROM GROUP_ID TO FALSE
        # CASE 2: add/change support group :group_id to BT
        # CASE 3: CHANGE COMPANY_IDS:
        """
        # CASE 1: ACTION CHANGE FROM GROUP_ID TO FALSE
        # ACT1: need remove current group_ids of BT out of :GROUP_ID
        group_to_update = []
        if 'group_id' in values and not values['group_id']:
            for BF_rec in self:
                if BF_rec.group_id:
                    group_to_update.append(BF_rec.group_id)
        # ACT1: remove
        res = super(ResCompanyType, self).write(values)

        # region after updated
        for group in group_to_update:
            self.process_group_id(group, True)


        for AF_rec in self:
            # CASE 2: add/change support group :group_id to BT
            # ACT2: need update :group_ids of this BT into :group_id
            if values.get('group_id') and AF_rec.group_id:
                AF_rec.process_group_id(AF_rec.group_id)

            # CASE 3: ADD/CHANGE :group_ids of BT
            if 'group_ids' in values:
                current_group_ids = AF_rec.group_ids.ids
                # ACT 3.1: Add current :group_ids to all of the company which belong to this BT.
                for company in AF_rec.company_ids:
                    company.group_ids = [(5, 0, 0), (6, 0, current_group_ids)]

                # ACT 3.2: Add current :group_ids to :group_id
                AF_rec.process_group_id(AF_rec.group_id)

            # CASE 3: CHANGE COMPANY_IDS:
            if 'company_ids' in values:
                AF_rec.onchange_company_ids()
        return res

    def process_group_id(self, group_obj, compute_user_groups_again=None):
        """
        Add :group_ids into :group_id.implied_ids
        Compute user's groups
        Compute user's company_ids
        """

        if group_obj.code != 'support':
            raise UserError("Your group must have code as support!")
        else:
            group_ids = []
            company_ids = []
            company_type_obj = self.env['res.company.type'].search([
                ('group_id', '=', group_obj.id)])
            for company_type in company_type_obj:
                group_ids += company_type.group_ids.ids
                company_ids += company_type.company_ids and company_type.company_ids.ids or []
            group_obj.implied_ids = [(5, 0, 0), (6, 0, group_ids)]
            _logger.info(f"ACTION ADD CHILD GROUPS TO SUPPORT GROUP {group_obj.name}: group_ids={group_ids}")

            #
            group_system_ids = find_user_system_ids(self)
            group_base = self.sudo().env.ref('base.group_user')
            user_group_ids = [group_base.id] + group_ids
            for user in group_obj.users:
                if user.id not in group_system_ids:
                    user_company_ids = [user.company_id.id] + company_ids
                    user.company_ids = [(5,0,0),(6, 0, user_company_ids)]
                    _logger.info(
                        f"ACTION ADD COMPANY_IDS TO USER OF SUPPORT GROUP {group_obj.name}: user_company_ids={user_company_ids}")
                    if compute_user_groups_again:
                        user.groups_id = [(5,0,0), (6, 0, user_group_ids)]
                        _logger.info(
                            f"ACTION ADD GROUPS_ID TO USER OF SUPPORT GROUP {group_obj.name}: user_group_ids={user_group_ids}")
