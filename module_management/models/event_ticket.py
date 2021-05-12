# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from math import copysign
from odoo.exceptions import UserError


class EventTicket(models.Model):
    _inherit = 'event.event.ticket'

    product_id = fields.Many2one('product.product', string='Product', required=True,
                                 domain=[("event_ok", "=", True)],
                                 default=False)
