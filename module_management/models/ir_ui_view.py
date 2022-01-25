# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class View(models.Model):
    _inherit = 'ir.ui.view'

    @api.model
    def _prepare_qcontext(self):
        self = self.sudo()
        return super(View, self)._prepare_qcontext()
