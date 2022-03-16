# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ReportSaleAccountMove(models.AbstractModel):
    _name = 'report.manufatory_dat_custom.report_sale_customer_invoices'

    @api.model
    def _get_report_values(self, docids, data=None):
        inv = None
        if len(data['records']) > 2:
            inv_id_str = data['records'][2]['id']
            inv_id = inv_id_str
            if '_' in inv_id_str:
                inv_id = inv_id_str.split('_')[-1]
            inv = self.env['account.move'].sudo().browse(int(inv_id))
            if not inv.partner_id:
                inv_id = inv_id_str.split('_')[0]
                inv = self.env['account.move'].sudo().browse(int(inv_id))
        res = {
            'doc_ids' : docids,
            'doc_model' : self.env['account.move'],
            'data' : data,
            'w_discount': data['w_discount'] or 0,
            'docs' : inv,
            'lines': data['records'],
        }
        return res
