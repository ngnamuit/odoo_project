# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from math import copysign
from odoo.exceptions import UserError
from odoo_project.module_management.controllers.main import ModuleManagementHome

SUPERUSER_ID = 2



class ModuleManagement(models.Model):
    _name = 'module.management'
    _description = 'Module Management'

    name = fields.Char(string='Name')


class ResCertification(models.Model):
    _name = 'res.certification'

    name = fields.Char(string='Name')


class ResCompany(models.Model):
    _inherit = 'res.company'

    #region define model fields
    company_code = fields.Char(string='Company Code')
    domain = fields.Char(string='Domain', compute="_compute_domain")
    established_year = fields.Integer(string='Established year')
    number_factories = fields.Integer(string='Number Factories')
    employees  = fields.Integer(string='Employees ')
    certification = fields.Char(string='Certification')
    product_categ_ids = fields.Many2many('product.category', string='Main Products')
    certification_ids = fields.Many2many('res.certification', string='Certification')
    brand = fields.Char(string='Brand')
    type = fields.Selection(
        [
            ('manufacturer', 'Manufacturer'),
            ('trading', 'Trading'),
            ('supplier', 'Supplier'),
            ('manufacturer_and_trading', 'Manufacturer & Trading'),
            ('other', 'Other'),
        ],
        default='manufacturer',
        string='Business Type',
    )
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
        # if 'group_ids' in values and 'user_ids' in values:
        #     res.group_ids.users = [(6, 0, res.user_ids.ids)]
        return res

    def write(self, values):
        company_code = values.get('company_code')
        if company_code:
            for rec in self:
                rec.validate_company_code(values)
        res = super(ResCompany, self).write(values)

        # case 1 add new user
        # case 2 remove user
        # case 3
        return res

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
                res.domain = base_url

    @api.depends('company_code')
    def get_user(self):
        if SUPERUSER_ID == self._uid:
            self.check_field = True
        else:
            self.check_field = False
    #endregion


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _default_company_id(self):
        user = self.env['res.users'].sudo().browse(self._uid)
        return user.company_id.id

    #region define fields
    company_id = fields.Many2one('res.company', 'Company', index=1,
                                 default=_default_company_id, readonly=1)

    #endregion

    #region CRUD
    def write(self, values):
        if self._uid != SUPERUSER_ID:
            for rec in self:
                if rec.company_id.id in [1, 2]:
                    raise UserError("You have no permission. Please contact admin for details!")
        return super(ProductTemplate, self).write(values)

    def unlink(self):
        if self._uid != SUPERUSER_ID:
            for rec in self:
                if rec.company_id.id in [1, 2]:
                    raise UserError("You have no permission. Please contact admin for details!")
        return super(ProductTemplate, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        print('Product Template Copy =========== ')
        self.ensure_one()
        default.update({'company_id': self.env.user.company_id.id})
        return super(ProductTemplate, self).copy(default=default)
    #endregion



class ProductProduct(models.Model):
    _inherit = 'product.product'

    #region CRUD
    def write(self, values):
        if self._uid != SUPERUSER_ID:
            for rec in self:
                if rec.company_id.id in [1, 2]:
                    raise UserError("You have no permission. Please contact admin for details!")
        return super(ProductProduct, self).write(values)

    def unlink(self):
        if self._uid != SUPERUSER_ID:
            for rec in self:
                if rec.company_id.id in [1, 2]:
                    raise UserError("You have no permission. Please contact admin for details!")
        return super(ProductProduct, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        print('Product Copy =========== ')
        self.ensure_one()
        if default is None:
            default = {}
        if 'name' not in default:
            default['name'] = _("%s (copy)") % self.name
        default.update({'company_id': self.env.user.company_id.id})
        return super(ProductProduct, self).copy(default=default)
    #endregion