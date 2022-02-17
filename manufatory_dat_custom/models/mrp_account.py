# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    has_posted_invoice = fields.Boolean(string="Has Posted Invoice", compute='_compute_has_posted_invoice', store=True)

    def _compute_has_posted_invoice(self):
        for record in self:
            post_record = self.env['account.move'].search([
                ('state', '=', 'posted'), ('partner_id', '=', record.id), ('move_type', 'in', ['out_invoice', 'in_refund'])
            ], limit=1)
            if post_record:
                record.has_posted_invoice = True
            else:
                record.has_posted_invoice = False

    def compute_has_posted_invoice(self):
        for partner in self.search([]):
            post_record = self.env['account.move'].search([
                ('state', '=', 'posted'), ('partner_id', '=', partner.id), ('move_type', 'in', ['out_invoice', 'in_refund'])
            ], limit=1)
            if post_record:
                partner.has_posted_invoice = True
            else:
                partner.has_posted_invoice = False


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def compute_product_bom_stand_price(self):
        """
        This function will compute standard_price of products/tempaltes which are type as manufactoring
        :return:
        """
        _logger.info("[compute_product_bom_stand_price] - START ....")
        # compute stand price for product
        product_need_to_compute = []  # list use to re-compute product a <- z after computed from a -> z
        products = self.env['product.product'].sudo().search([('type', '!=', 'service')])
        for product in products:
            if product.id == 47:
                _logger.info(f"bom_count == {product.bom_count}, valuation == {product.valuation}, cost_method == {product.cost_method}")
            if product.bom_count == 0 or (product.valuation == 'real_time' and product.cost_method == 'fifo'):
                continue
            else:
                _logger.info("[compute_product_bom_stand_price] - product = %s", product)
                product.button_bom_cost()
                product_need_to_compute.insert(0, product)

        _logger.info("[compute_product_bom_stand_price] - product_need_to_compute = %s", product_need_to_compute)
        for product in product_need_to_compute:
            _logger.info("[compute_product_bom_stand_price] - ReCompute for product = %s", product)
            product.button_bom_cost()

        # compute stand price for template
        templates_need_to_compute = []
        templates = self.env['product.template'].sudo().search([('type', '!=', 'service')])
        for template in templates:
            if template.bom_count == 0 or (template.valuation == 'real_time' and template.cost_method == 'fifo'):
                continue
            else:
                template.button_bom_cost()
                templates_need_to_compute.append(template)
        _logger.info("[compute_product_bom_stand_price] - templates_need_to_compute = %s", templates_need_to_compute)
        _logger.info("[compute_product_bom_stand_price] - .... DONE")
