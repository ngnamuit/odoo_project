# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from math import copysign
from odoo.exceptions import UserError

SUPERUSER_ID = 2

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
