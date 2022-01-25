# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _
from math import copysign
from odoo.exceptions import UserError
from odoo.addons.module_management.controllers.main import ModuleManagementHome
_logger = logging.getLogger(__name__)
SUPERUSER_ID = 2


def find_user_system_ids(self):
    group_erp_manager = self.sudo().env.ref('base.group_erp_manager')
    group_system = self.sudo().env.ref('base.group_system')
    return group_erp_manager.users.ids + group_system.users.ids


class ResCompany(models.Model):
    _inherit = 'res.company'

    #region define model fields
    active = fields.Boolean(string='Active', default=True)
    company_code = fields.Char(string='Company Code')
    domain = fields.Char(string='Domain', compute="_compute_domain")
    established_year = fields.Integer(string='Established year')
    number_factories = fields.Integer(string='Number Factories')
    employees  = fields.Integer(string='Employees')
    certification = fields.Char(string='Certification')
    product_categ_ids = fields.Many2many('product.category', string='Main Products')
    certification_ids = fields.Many2many('res.certification', string='Certification')
    brand = fields.Char(string='Brand')
    type_id = fields.Many2one('res.company.type', string='Business Type')
    check_field = fields.Boolean('Check field', compute='get_user')
    group_ids = fields.Many2many('res.groups', string='Groups')

    #endregion

    #region CRUD
    def unlink(self):
        if self._uid != SUPERUSER_ID:
            raise UserError("You have no permission. Please contact admin for details!")
        return super(ResCompany, self).unlink()

    @api.model
    def create(self, values):
        self.validate_company_code(values)
        if self._uid != SUPERUSER_ID:
            user = self.env['res.users'].sudo().browse(self._uid)[0]
            is_company = user.company_id and user.company_id.id not in [1, 2] and True or False
            if is_company:
                raise UserError("You can not create more company. Please contact admin for details!")
        res = super(ResCompany, self).create(values)
        type_obj = res.type_id
        if type_obj:
            type_obj.onchange_company_ids()
        res.onchange_type_id()
        return res

    def write(self, values):
        company_code = values.get('company_code')
        if company_code:
            for rec in self:
                rec.validate_company_code(values)
        res = super(ResCompany, self).write(values)
        for rec in self:
            # CASE: change :type_id -> it make change :group_ids
            if 'group_ids' in values:
                _logger.info(f"ACTION CHANGE GROUP: group_ids={rec.group_ids and rec.group_ids.ids or rec.group_ids}")
                rec.action_change_group()
                _logger.info(f"ACTION CHANGE GROUP: DONE")
            if 'type_id' in values:
                type_obj = rec.type_id
                if type_obj:
                    type_obj.onchange_company_ids()
                rec.onchange_type_id()
        return res

    def action_change_group(self):
        users_model = self.env['res.users']
        user_ids, admin_ids = self.find_company_user_id()
        user_group_ids, admin_group_ids = self.find_group_id_base_on_code()
        if user_ids:
            users = users_model.browse(user_ids)
            if user_group_ids:
                users.write(
                    {'groups_id': [(6, 0, user_group_ids)]}
                )
                _logger.info(f"START ACTION CHANGE GROUP - UPDATE: "
                             f"user_ids={user_ids}, user_group_ids={user_group_ids}")
            else:
                users.write(
                    {'groups_id': [(5, 0, 0)]}
                )
                _logger.info(f"START ACTION CHANGE GROUP - DELETED: "
                             f"user_ids={user_ids}")
        if admin_ids:
            users = users_model.browse(admin_ids)
            if admin_group_ids:
                users.write(
                    {'groups_id': [(6, 0, admin_group_ids)]}
                )
                _logger.info(f"START ACTION CHANGE GROUP - UPDATE: "
                             f"admin_ids={admin_ids}, admin_group_ids={admin_group_ids}")
            else:
                users.write(
                    {'groups_id': [(5, 0, 0)]}
                )
                _logger.info(f"START ACTION CHANGE GROUP - DELETED: "
                             f"admin_ids={admin_ids}")
        return True

    def find_group_id_base_on_code(self):
        user_group_ids = []
        admin_group_ids = []
        for group in self.group_ids:
            if group.code == 'user':
                user_group_ids.append(group.id)
            else:
                admin_group_ids.append(group.id)
        admin_group_ids += user_group_ids
        return user_group_ids, admin_group_ids

    def find_company_user_id(self):
        user_ids = []
        admin_ids = []
        for user in self.user_ids:
            if user.id not in [1, 2] and user.group_type == 'user':
                user_ids.append(user.id)
            elif user.id not in [1, 2] and user.group_type == 'admin':
                admin_ids.append(user.id)
        return user_ids, admin_ids

    def read(self, fields=None, load='_classic_read'):
        # NEED TO CUSTOM HERE
        return super(ResCompany, self).read(fields=fields, load=load)
    #endregion

    #region for other functions
    def validate_company_code(self, values):
        company_code = values.get('company_code')
        if company_code:
            ex_company_code = self.env['res.company'].sudo().search([('company_code', '=', company_code)])
            if ex_company_code:
                raise UserError("Your company code has existed already. Please choose another company code!")
        return True

    @api.depends('company_code')
    def _compute_domain(self):
        base_url = ModuleManagementHome().get_base_url(self)
        for res in self:
            if res.company_code:
                res.domain = f"{res.company_code}.{base_url}"
            else:
                res.domain = f"{base_url}"

    @api.depends('company_code')
    def get_user(self):
        if SUPERUSER_ID == self._uid:
            self.check_field = True
        else:
            self.check_field = False

    def onchange_type_id(self):
        group_ids = self.type_id.group_ids.ids
        if self.type_id:
            self.group_ids = [(6, 0, group_ids)]
        else:
            self.group_ids = [(5, 0, 0)]
    #endregion


class ResCertification(models.Model):
    _name = 'res.certification'

    name = fields.Char(string='Name')