# -*- coding: utf-8 -*-
from odoo.addons.web.controllers.main import Home
from odoo.addons.website.controllers.main import Website
import odoo
import odoo.modules.registry
from odoo.http import content_disposition, dispatch_rpc, request, Response
import werkzeug
from odoo import http, tools

BASE_ULR = 'bnidx.net'

class ModuleManagementHome(Home):

    def _get_host(self, request):
        return request.httprequest.environ.get('HTTP_HOST', '').replace("http://", "").replace("https://", "")

    def get_base_url(self, request):
        if 'localhost' in request.env['ir.config_parameter'].sudo().get_param('web.base.url', default='localhost:8069'):
            return 'localhost:8069'
        else:
            return BASE_ULR

    def _get_user_sub_domain(self, user):
        return user.company_id.domain.replace("http://", "").replace("https://", "")

    def _login_redirect(self, uid, redirect=None):
        user = request.env['res.users'].sudo().browse(uid)
        host = self._get_host(request)
        print(f"_login_redirect self ====== {request}")
        print(f"_login_redirect USER ====== {user}")
        print(f"_login_redirect PARAMS ====== {host}, {user.company_id.domain}")
        if user and user.id not in [odoo.SUPERUSER_ID,2] and host != self._get_user_sub_domain(user):
            request.session.logout()
            werkzeug.utils.redirect('/web/login', 303)
        return super(ModuleManagementHome, self)._login_redirect(uid, redirect)


    def _check_domain(self, request):
        host = self._get_host(request)
        base_url = self.get_base_url(request)
        print(f"[CHECK_DOMAIN] host={host} \n base_url={base_url}")
        if host != base_url:
            sub_domain = host.split('.')[0]
            ex_sub_domain = request.env['res.company'].sudo().search([('company_code', '=', sub_domain)])
            if not ex_sub_domain:
                print(f"[CHECK_DOMAIN] Can not found domain={sub_domain}")
                raise request.not_found()
        return True

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        self._check_domain(request)
        return super(ModuleManagementHome, self).web_login(redirect, **kw)

    @http.route('/', type='http', auth="none")
    def index(self, s_action=None, db=None, **kw):
        self._check_domain(request)
        return http.local_redirect('/web', query=request.params, keep_hash=True)

    @http.route('/web', type='http', auth="none")
    def web_client(self, s_action=None, **kw):
        self._check_domain(request)
        return super(ModuleManagementHome, self).web_client(s_action, **kw)
