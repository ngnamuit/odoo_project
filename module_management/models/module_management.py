# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from math import copysign


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

