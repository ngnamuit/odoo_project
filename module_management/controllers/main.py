# -*- coding: utf-8 -*-
from odoo.addons.web.controllers.main import Home
import odoo
import odoo.modules.registry
from odoo.http import content_disposition, dispatch_rpc, request, Response
import werkzeug

class ModuleManagementHome(Home):

    def _login_redirect(self, uid, redirect=None):
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        user = request.env['res.users'].sudo().browse(uid)
        if user and user.id not in [odoo.SUPERUSER_ID,2] and user.company_id.domain != base_url:
            request.session.logout()
            werkzeug.utils.redirect('/web/login', 303)
            # redirect to login page
            # values = request.params.copy()
            # try:
            #     values['databases'] = http.db_list()
            # except odoo.exceptions.AccessDenied:
            #     values['databases'] = None
            #     values['error'] = _("Wrong login/password")
            # response = request.render('web.login', values)
            # response.headers['X-Frame-Options'] = 'DENY'
            # return response
        return super(ModuleManagementHome, self)._login_redirect(uid, redirect)