# -*- coding: utf-8 -*-
# thư mục /opt/odoo14/odoo_source_dat/, username: root, pw: .)/NzT*fLu\(uBNIDX\82[64JFF@$$#
# scp -r manufatory_dat_custom/ root@103.221.221.109:/opt/odoo14/odoo_source_dat/custom
# $pbkdf2-sha512$25000$cg4BwPg/h/DeG0OoNcY4Rw$/fq5iO4r7BmW1NsJwHml1tB6WqY3feAmhJxSEEYPPYq2m8ZWsstvoot6H5HOvKntNjCRJaZZWCV.53ZNLeWEng
{
    'name': 'Manufactoring DAT Customs',
    'version': '1.0',
    'category': 'Tools',
    'description': "",
    'website': '',
    'summary': '',
    'sequence': 45,
    'depends': [
        'base',
        'account',
        'web',
        'mrp',
        'mrp_account',
        'sale'
    ],
    'data': [
        'data/ir_cron.xml',
        'data/paperformat_report.xml',
        'sercurity/ir.model.access.csv',
        'report/report_deliveryslip.xml',
        'report/report_template.xml',
        'report/sale_report.xml',
        'report/invoice_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
