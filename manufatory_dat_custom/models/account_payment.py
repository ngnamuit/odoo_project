# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = "account.payment"

    notes = fields.Char('Notes')
