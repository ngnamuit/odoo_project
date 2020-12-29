# -*- coding: utf-8 -*-
from odoo.addons.web.controllers.main import Home
import odoo
import odoo.modules.registry
from odoo.http import content_disposition, dispatch_rpc, request, Response
import werkzeug

class ModuleManagementHome(Home):

    def _login_redirect(self, uid, redirect=None):
        user = request.env['res.users'].sudo().browse(uid)
        host = request.httprequest.environ.get('HTTP_HOST', '')
        print(f"_login_redirect self ====== {request}")
        print(f"_login_redirect USER ====== {user}")
        print(f"_login_redirect PARAMS ====== {host}, {user.company_id.domain}")
        if user and user.id not in [odoo.SUPERUSER_ID,2] and host != user.company_id.domain.replace("http://", "").replace("https://", ""):
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