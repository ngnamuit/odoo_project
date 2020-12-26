# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from math import copysign
from odoo.exceptions import UserError

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

    company_code = fields.Char(string='Company Code')
    domain = fields.Char(string='Domain')
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

    def unlink(self):
        if self._uid != SUPERUSER_ID:
            raise UserError("You have no permission. Please contact admin for details!")
        return super(ResCompany, self).unlink()

    @api.depends('company_code')
    def get_user(self):
        if SUPERUSER_ID == self._uid:
            self.check_field = True
        else:
            self.check_field = False

    @api.model
    def create(self, values):
        if self._uid != SUPERUSER_ID:
            user = self.env['res.users'].sudo().browse(self._uid)[0]
            is_company = user.company_id and user.company_id.id not in [1, 2] and True or False
            if is_company:
                raise UserError("You can not create more company. Please contact admin for details!")
        return super(ResCompany, self).create(values)

    def read(self, fields=None, load='_classic_read'):
        # NEED TO CUSTOM HERE
        print("READ ==== ")
        return super(ResCompany, self).read(fields=fields, load=load)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _default_company_id(self):
        user = self.env['res.users'].sudo().browse(self._uid)
        return user.company_id.id

    # define fields
    company_id = fields.Many2one('res.company', 'Company', index=1,
                                 default=_default_company_id, readonly=1)