# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import io
import logging
import os
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, UserError
from odoo.modules.module import get_resource_path

from random import randrange
from PIL import Image

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_currency_usd_id(self):
        currency = self.env["res.currency.rate"].search([('id', '=', 2)])
        for line in self:
            if currency:
                line.currency_usd_id = currency.id

    currency_usd_id = fields.Many2one('res.currency', compute='_compute_currency_usd_id')


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    advance_payment_method = fields.Selection(
        selection_add=[('medco_percentage', 'Medco Down payment (percentage)')],
        ondelete={'medco_percentage': 'cascade'},
        string='Create Invoice', default='delivered', required=True,
        help="A standard invoice is issued with all the order lines ready for invoicing, \
            according to their invoicing policy (based on ordered or delivered quantity)."
    )

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        if self.advance_payment_method in ['percentage', 'medco_percentage']:
            amount = self.default_get(['amount']).get('amount')
            return {'value': {'amount': amount}}
        else:
            return super(SaleAdvancePaymentInv, self).onchange_advance_payment_method()


    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        if self.advance_payment_method == 'medco_percentage':
            for order in sale_orders:
                if self.product_id.invoice_policy != 'order':
                    raise UserError(_(
                        'The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
                if self.product_id.type != 'service':
                    raise UserError(_(
                        "The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
                self._medco_create_invoice(order, order.order_line)
            return {'type': 'ir.actions.act_window_close'}
        else:
            return super(SaleAdvancePaymentInv, self).create_invoices()

    def _medco_create_invoice(self, order, so_lines):
        if self.amount <= 0.00:
            raise UserError(_('The value of the down payment amount must be positive.'))

        invoice_vals = self._medco_prepare_invoice_values(order, so_lines)

        if order.fiscal_position_id:
            invoice_vals['fiscal_position_id'] = order.fiscal_position_id.id
        invoice = self.env['account.move'].sudo().create(invoice_vals).with_user(self.env.uid)
        invoice.message_post_with_view('mail.message_origin_link',
                    values={'self': invoice, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return invoice


    def _medco_prepare_invoice_values(self, order, so_lines):
        invoice_line_ids = []
        for so_line in so_lines:
            invoice_line_ids.append(
                (0, 0, {
                    'name': so_line.name,
                    'price_unit': (self.amount * so_line.price_unit) / 100,
                    'quantity': so_line.product_uom_qty,
                    'product_id': so_line.product_id.id,
                    'product_uom_id': so_line.product_uom.id,
                    'tax_ids': [(6, 0, so_line.tax_id.ids)],
                    'sale_line_ids': [(6, 0, [so_line.id])],
                    'analytic_tag_ids': [(6, 0, so_line.analytic_tag_ids.ids)],
                    'analytic_account_id': order.analytic_account_id.id or False,
                })
            )
        invoice_vals = {
            'ref': order.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': order.name,
            'invoice_user_id': order.user_id.id,
            'narration': order.note,
            'partner_id': order.partner_invoice_id.id,
            'fiscal_position_id': (order.fiscal_position_id or order.fiscal_position_id.get_fiscal_position(order.partner_id.id)).id,
            'partner_shipping_id': order.partner_shipping_id.id,
            'currency_id': order.pricelist_id.currency_id.id,
            'payment_reference': order.reference,
            'invoice_payment_term_id': order.payment_term_id.id,
            'partner_bank_id': order.company_id.partner_id.bank_ids[:1].id,
            'team_id': order.team_id.id,
            'campaign_id': order.campaign_id.id,
            'medium_id': order.medium_id.id,
            'source_id': order.source_id.id,
            'invoice_line_ids': invoice_line_ids,
        }

        return invoice_vals
