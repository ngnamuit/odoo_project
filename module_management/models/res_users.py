# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from math import copysign
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)
SUPERUSER_ID = 2


class ResUsers(models.Model):
    _inherit = 'res.users'

    group_type = fields.Selection(
        [
            ('user', 'User'),
            ('admin', 'Admin'),
        ], string="Group Type", default='user')
    internal = fields.Boolean('Internal User', default=False)
    group_id = fields.Many2one('res.groups', 'Group')

    @api.model
    def create(self, values):
        res = super(ResUsers, self).create(values)

        # CASE 1: create external user
        if res.internal is False:
            res.add_groups()
        # CASE 2: create internal user
        elif res.internal is True and res.group_id:
            res.add_company_ids_to_user()
            res.groups_id = [(5, 0, 0)]  # clear all groups of user before that
            res.group_id.users = [(4, res.id)]
        return res

    def add_company_ids_to_user(self):
        company_ids = []
        if self.group_id:
            company_type_obj = self.env['res.company.type'].search([('group_id', '=', self.group_id.id)])
            for company_type in company_type_obj:
                company_ids += company_type.company_ids.ids
        _logger.info(f"START ADD COMPANY TO USER: company_ids={company_ids}")
        if company_ids:
            company_ids.append(self.env.user.company_id.id)
            self.company_ids = [(5, 0, 0), (6, 0, company_ids)]

    def write(self, values):
        # ACTION: change group_id to NONE -> need to remove all groups of user before that
        if 'group_id' in values and not values.get('group_id'):
            for rec in self:
                if rec.group_id:
                    group_ids = []
                    group_base = self.sudo().env.ref('base.group_user')
                    group_ids.append(group_base.id)
                    values['groups_id'] = [(6, 0, group_ids)]
        res = super(ResUsers, self).write(values)
        # CASE 1: Action of a user that have subdomain
        # note: company_id: default self.user.company_id (user's updating), group_type must be user or admin
        if 'group_type' in values or 'company_id' in values:
            for rec in self:
                if rec.internal is False:  #
                    rec.add_groups()

        # CASE 2: Action of a user that belong to domain
        # change to internal user and add new group_id (that mean as change user to support for specific business type)
        if values.get('internal', False) is True or values.get('group_id'):
            for rec in self:
                if rec.group_id or rec.internal:
                    rec.add_company_ids_to_user()
                    rec.groups_id = [(5, 0, 0)]   # clear all of user's groups before that
                    rec.group_id.users = [(4, rec.id)]
        return res

    def add_groups(self):
        # region to find groups that will be add when a users is created
        _logger.info(f"ACTION ADD USER: START")
        group_ids = []
        group_base = self.sudo().env.ref('base.group_user')
        group_ids.append(group_base.id)

        # find groups that group's type is equal to user.group_type to append to group_ids
        company_group_ids = self.company_id and self.company_id.group_ids or []
        for group in company_group_ids:
            if self.group_type == 'admin':
                group_ids = company_group_ids.ids
            elif self.group_type == 'user' and group.code == self.group_type:
                group_ids.append(group.id)
        # endregion

        self.groups_id = [(6, 0, group_ids)]
        _logger.info(f"ACTION ADD USER - UPDATED: user.login={self.login}, group_ids={group_ids}")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    signup_token = fields.Char(copy=False, groups="base.group_user")
    signup_type = fields.Char(string='Signup Token Type', copy=False, groups="base.group_user")
    signup_expiration = fields.Datetime(copy=False, groups="base.group_user")