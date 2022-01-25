# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class SaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"
    _description = "Sale Order Line"

    @api.depends('price_unit')
    def _compute_gross_amount(self):
        currency = self.env["res.currency.rate"].search([('id', '=', 2)])
        for line in self:
            line.price_usd = line.price_unit / currency.rate

    price_usd = fields.Float(string="Amount (USD)", compute='_compute_gross_amount', readonly=True, store=True)

