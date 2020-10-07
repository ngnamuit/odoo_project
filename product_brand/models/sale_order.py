from lxml import etree

from odoo import api, models, _, fields
from odoo.exceptions import AccessError, RedirectWarning, UserError
from odoo.tools import ustr


class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_contact_name = fields.Char(string='Customer Contact Name')

    def action_send_so_summary(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env.ref('product_brand.email_template_sale_order_summary').id
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, 'sale.order', self.ids[0])
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_send_so_details(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env.ref('product_brand.email_template_sale_order_details').id
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_template(template.lang, 'sale.order', self.ids[0])
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu
        )
        if view_type == 'form':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//button[@name='action_quotation_send']"):
                node.set('invisible', "1")

        if res.get('toolbar', False) and res.get('toolbar').get('print', False):
            reports = res.get('toolbar').get('print')
            for report in reports:
                if report.get('report_file', False) and report.get('report_file') == 'sale.report_saleorder':
                    res['toolbar']['print'].remove(report)
        return res
