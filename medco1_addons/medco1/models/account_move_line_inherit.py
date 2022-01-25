# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class AccountMoveLineInherit(models.Model):
    _inherit = "account.move.line"
    _description = "Account Move Line"

    @api.depends('quantity', 'price_unit')
    def _compute_gross_amount(self):
        currency = self.env["res.currency.rate"].search([('id', '=', 2)])
        for line in self:
            line.price_usd = line.price_unit / currency.rate

    price_usd = fields.Float(string="Amount (USD)", compute='_compute_gross_amount', readonly=True, store=True)



