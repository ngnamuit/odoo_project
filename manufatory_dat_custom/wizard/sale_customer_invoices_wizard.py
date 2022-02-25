# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError, ValidationError


# FORMAT DATE
format_date = '%m %Y'
format_datetime = '%d/%m/%Y'
class SaleCustomerWizard(models.TransientModel):
    _name = 'sale.customer.invoices.wizard'

    # General
    partner_id = fields.Many2one('res.partner', string='Partner', domain="[('has_posted_invoice', '=', True)]")
    from_date = fields.Date(string='From Date')
    to_date = fields.Date(string='To Date')
    discount = fields.Float(string="% Discount")

    def get_datas(self):
        sql = """
            WITH A as (
                SELECT mo_ori.id, 
                        mo_ori.name as name, 
                        res.name AS customer,
                        mo_ori.name AS number_invoice, 
                        mo_ori.invoice_date,
                        CASE WHEN move_type = 'out_refund' THEN (-1) * mo_ori.amount_total 
                             ELSE mo_ori.amount_total 
                          END AS amount_vnd, 
                        0 as amount_paid_vnd,
                        CASE WHEN move_type = 'out_refund' THEN (-1) * mo_ori.amount_total 
                            ELSE mo_ori.amount_total 
                          END as amount_remain_vnd,
                        mo_ori.date AS payment_date,
                        aml.name as product_name,
                        CASE WHEN move_type = 'out_refund' THEN (-1) * aml.quantity 
                            ELSE aml.quantity 
                          END as product_qty,
                        CASE WHEN move_type = 'out_refund' THEN (-1) * aml.discount
                             ELSE aml.discount
                          END as product_discount,
                        CASE WHEN move_type = 'out_refund' THEN aml.price_unit 
                             ELSE aml.price_unit 
                          END as product_price_unit,
                        CASE WHEN move_type = 'out_refund' THEN (-1) *  aml.price_subtotal
                             ELSE aml.price_subtotal
                          END as price_subtotal
                FROM account_move mo_ori
                INNER JOIN account_move_line aml on aml.move_id = mo_ori.id
                INNER JOIN product_product pp on pp.id = aml.product_id
                LEFT JOIN account_journal aj ON mo_ori.journal_id = aj.id
                LEFT JOIN res_partner res ON res.id = mo_ori.partner_id
                LEFT JOIN account_payment ap ON mo_ori.payment_id = ap.id
                LEFT JOIN account_payment_register apr ON ap.id = apr.id
                WHERE mo_ori.partner_id = {0} and mo_ori.state = 'posted' AND (move_type = 'out_invoice' OR move_type = 'in_refund' or move_type = 'out_refund') 

            )
            select 
                        distinct CONCAT(ac.id::text, '_', am.id::text) as id, 
                        am.name as name, 
                        '' AS customer,
                        am.name as number_invoice, 
                        am.date as invoice_date,
                        0 AS amount_vnd, 
                        ac.amount as amount_paid_vnd,
                        A.amount_vnd - ac.amount as amount_remain_vnd,
                        am.date AS payment_date,
                        '' as product_name,
                        0 as product_qty,
                        0 as product_discount,
                        0 as product_price_unit,
                        0 as price_subtotal
                from account_payment ac 
                inner join account_move am on am.id = ac.move_id
                inner join A on A.name = am.ref
                where am.state = 'posted' and am.date <= '{1}' and am.date >= '{2}'
              union 
            select  A.id::text as id,
                    A.name,
                    A.customer,
                    A.number_invoice,
                    A.invoice_date,
                    A.amount_vnd,
                    A.amount_paid_vnd,
                    A.amount_remain_vnd,
                    A.payment_date,
                    A.product_name,
                    A.product_qty,
                    A.product_discount,
                    A.product_price_unit,
                    A.price_subtotal
            from A
            WHERE A.invoice_date <= '{1}' and A.invoice_date >= '{2}'
            ORDER BY invoice_date asc, 2 asc;
        """.format(self.partner_id.id, self.to_date, self.from_date)
        self.env.cr.execute(sql)

        records = self.env.cr.dictfetchall()
        return records

    def get_ton(self):
        sql = """
            WITH A AS (
                SELECT res.name AS customer,
                    CASE WHEN move_type = 'out_refund' THEN (-1) * mo_ori.amount_total 
                         ELSE mo_ori.amount_total  
                      END AS amount_vnd, 
                    CASE WHEN move_type = 'out_refund' THEN (-1) * (mo_ori.amount_total - mo_ori.amount_residual)
                         ELSE mo_ori.amount_total - mo_ori.amount_residual 
                      END AS amount_paid_vnd,
                    CASE WHEN move_type = 'out_refund' THEN (-1) * mo_ori.amount_residual 
                         ELSE mo_ori.amount_residual
                      END AS amount_remain_vnd
                FROM account_move mo_ori
                LEFT JOIN account_journal aj ON mo_ori.journal_id = aj.id
                LEFT JOIN res_partner res ON res.id = mo_ori.partner_id
                LEFT JOIN account_payment ap ON mo_ori.payment_id = ap.id
                LEFT JOIN account_payment_register apr ON ap.id = apr.id
                WHERE mo_ori.partner_id = %s and mo_ori.invoice_date < '%s' 
                        and mo_ori.state = 'posted' AND (move_type = 'out_invoice' OR move_type = 'in_refund' or move_type = 'out_refund') 
            )
            select customer,
                    SUM(amount_vnd) as amount_vnd,
                    SUM(amount_paid_vnd) as amount_paid_vnd,
                    SUM(amount_remain_vnd) as amount_remain_vnd
            from A
            group by 1;
        """%(self.partner_id.id, self.from_date)
        self.env.cr.execute(sql)
        record = self.env.cr.dictfetchone()
        format_date = '%d-%m-%Y'

        sql2 = """
            WITH A as (
                SELECT mo_ori.name AS name,
                       move_type as move_type
                FROM account_move mo_ori
                LEFT JOIN account_journal aj ON mo_ori.journal_id = aj.id
                LEFT JOIN res_partner res ON res.id = mo_ori.partner_id
                LEFT JOIN account_payment ap ON mo_ori.payment_id = ap.id
                LEFT JOIN account_payment_register apr ON ap.id = apr.id
                WHERE mo_ori.partner_id = %s
                        and mo_ori.state = 'posted' AND (move_type = 'out_invoice' OR move_type = 'in_refund' OR move_type = 'out_refund') 
            
            )
            select SUM(
                CASE WHEN A.move_type = 'out_refund' THEN (-1) * ac.amount
                     ELSE ac.amount END
            ) as amount_paid_vnd
            from account_payment ac 
                inner join account_move am on am.id = ac.move_id
                inner join A on A.name = am.ref
                where am.state = 'posted' and am.date < '%s'
        """%(self.partner_id.id, self.from_date)
        self.env.cr.execute(sql2)
        record2 = self.env.cr.dictfetchone()
        return {
            'invoice_date': self.from_date.strftime(format_date),
            'amount_vnd': record['amount_vnd'] if record else 0,
            'amount_paid_vnd': (record2.get('amount_paid_vnd', 0) if record2 else 0) or 0,
            'amount_remain_vnd': record['amount_remain_vnd'] if record else 0,
        }

    def remake_data(self, records, ton):
        result = []
        discount = 0
        # write ton record
        result.append({
            'ngay': '',
            'ctu': '',
            'noi_dung': 'TỒN TỪ TRƯỚC {0}'.format(ton['invoice_date']),
            'sl': '',
            'km': '',
            'dgia': '',
            'ck': '',
            'tm': '',
            'tien_hang': '{:0,.0f}'.format(ton['amount_vnd']) or '',
            'kh_tra': '{:0,.0f}'.format(ton['amount_paid_vnd']) or '',
            'con_lai': '{:0,.0f}'.format(ton['amount_remain_vnd']) or '',
        })

        # define for last line
        year_month = []
        invoice_ids = []
        invoice_invoice_kh_tra = {}
        sum_tien_hang = 0 + (ton.get('amount_vnd', 0) or 0)
        sum_kh_tra = 0 + (ton.get('amount_paid_vnd', 0) or 0)
        sum_tien_con_lai = (sum_tien_hang - sum_kh_tra) or 0

        # write invoice lines
        for record in records:
            # region for define params
            inv_id = record['id']
            invoice_kh_tra = record['amount_paid_vnd']
            inv_date = record['invoice_date'].strftime(format_date)

            # check and update
            if inv_id not in invoice_ids:
                invoice_invoice_kh_tra.update({str(inv_id): invoice_kh_tra})

            # update line sum_line_con_lai, sum_tien_hang
            line, tien_hang, kh_tra = self.compute_line(record, invoice_invoice_kh_tra)
            sum_tien_con_lai_for_month = sum_tien_con_lai
            sum_tien_con_lai = sum_tien_con_lai + tien_hang - kh_tra
            sum_tien_hang = sum_tien_hang + tien_hang
            line['con_lai'] = '{:0,.0f}'.format(sum_tien_con_lai)

            # write month record
            if inv_date not in year_month:
                year_month.append(inv_date)
                result.append({
                    'ngay': '',
                    'ctu': '',
                    'noi_dung': 'THÁNG {0}'.format(inv_date),
                    'sl': '',
                    'km': '',
                    'dgia': '',
                    'ck': '',
                    'tm': '',
                    'tien_hang': '-',
                    'kh_tra': '',
                    'con_lai': '{:0,.0f}'.format(sum_tien_con_lai_for_month) or '',
                })
                result.append(line)
                invoice_ids.append(inv_id)

            else:
                # write first line of invoice
                if inv_id not in invoice_ids:
                    invoice_ids.append(inv_id)
                else:
                    line['ngay'] = ''
                    line['ctu'] = ''
                result.append(line)

        if records:
            last = {
                'ngay': '',
                'ctu': '',
                'noi_dung': '',
                'sl': '',
                'km': '',
                'dgia': '',
                'ck': '',
                'tm': '',
                'tien_hang': '' ,#'{:0,.0f}'.format(sum_tien_hang or 0),
                'kh_tra': '', #'{:0,.0f}'.format((sum_tien_hang - sum_tien_con_lai) or 0),
                'con_lai': '{:0,.0f}'.format(sum_tien_con_lai),
            }
            result.append(last)
            import copy
            last_line = copy.deepcopy(last)
            discount = ((self.discount or 0) * ((sum_tien_hang - sum_tien_con_lai) or 0)) * 0.01
            must_paid = sum_tien_con_lai - round(discount)
            last_line.update({
                'tien_hang': '{:0,.0f}'.format(sum_tien_hang or 0),
                'kh_tra': '{:0,.0f}'.format((sum_tien_hang - sum_tien_con_lai) or 0),
                'con_lai': '',
                'discount': '{:0,.0f}'.format(discount) if discount else '0',
                'must_paid': '{:0,.0f}'.format(must_paid) if must_paid else '0'
            })
            result.append(last_line)

        return result

    def compute_line(self, record, invoice_invoice_kh_tra):
        tien_hang = record['price_subtotal']
        con_lai = 0
        kh_tra = 0
        invoice_id = record['id']
        invoice_kh_tra = invoice_invoice_kh_tra.get(str(invoice_id)) or 0
        if invoice_kh_tra <= 0:
            kh_tra = 0
            con_lai = kh_tra
        else:
            if invoice_kh_tra <= tien_hang:
                kh_tra = invoice_kh_tra
                con_lai = 0
            else:
                kh_tra = tien_hang if tien_hang > 0 else invoice_kh_tra
                con_lai = invoice_kh_tra - tien_hang
        invoice_invoice_kh_tra[str(invoice_id)] = con_lai
        inv_datetime = record['invoice_date'].strftime(format_datetime)
        line = {
            'id': record['id'],
            'ngay': inv_datetime,
            'ctu': record['number_invoice'],
            'noi_dung': record['product_name'],
            'sl': '{:0,.0f}'.format(record['product_qty']) if record['product_qty'] else '',
            'km': '',
            'dgia': '{:0,.0f}'.format(record['product_price_unit']) if record['product_price_unit'] else '',
            'ck': str('{:0,.0f}'.format(record.get('product_discount'))) + '%' if record.get('product_discount') else '',
            'tm': '',
            'tien_hang': '{:0,.0f}'.format(tien_hang) if tien_hang else '',
            'kh_tra': '{:0,.0f}'.format(kh_tra) if kh_tra else '',
            'con_lai': '{:0,.0f}'.format(con_lai) if con_lai else '',
        }
        return line, tien_hang, kh_tra

    def print_report(self):
        self.ensure_one()
        # validate
        current_date = date.today()
        if self.discount and (self.discount > 100 or self.discount < 0):
            raise UserError(_('% Discount is invalid'))
        if not self.from_date or self.from_date >= current_date or (self.from_date >= self.to_date):
            raise UserError(_('From Date or To Date is invalid'))

        records = self.get_datas()
        ton = self.get_ton()
        remake_data = self.remake_data(records, ton)
        partner = [self.partner_id]
        company = [self.env.user.company_id]
        datas = {
            'w_discount': self.discount or 0,
            'model': 'sale.customer.invoices.wizard',
            'form': [1],
            'partner': partner,
            'company': company,
            'records': remake_data
        }
        report = self.env.ref('manufatory_dat_custom.action_report_sale_customer_invoices').sudo()
        return report.report_action(self, data=datas)
