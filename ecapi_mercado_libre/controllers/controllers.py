# -*- coding: utf-8 -*-
from odoo import http, exceptions, _
from odoo.http import request
import odoo
import logging
import json
import werkzeug
import requests
import dateutil.parser
import pytz

_logger = logging.getLogger(__name__)


class Omna(http.Controller):
    @http.route('/omna/sign_in/', type='http', auth='user')
    def sing_in(self, code, **kw):
        request.env.user.context_omna_get_access_token_code = str(code)
        action = request.env.ref('ecapi_mercado_libre.action_omna_orders').read()[0]
        return werkzeug.utils.redirect('/web#action=%s' % action['id'] or '', 301)

    @http.route('/omna/get_access_token/', type='json', auth='user', methods=['POST'], csrf=False)
    def get_access_token(self, default_tenant=None, **kw):
        request.env.user.context_omna_get_access_token_code = None
        if default_tenant and default_tenant.get('id', False):
            tenant = request.env["omna.tenant"].search([('omna_tenant_id', '=', default_tenant.get('id'))])
            tzinfos = {
                'PST': -8 * 3600,
                'PDT': -7 * 3600,
            }
            if tenant:
                tenant.write({
                    'name': default_tenant.get('name'),
                    'token': default_tenant.get('token'),
                    'secret': default_tenant.get('secret'),
                    'is_ready_to_omna': default_tenant.get('is_ready_to_omna'),
                    'deactivation': odoo.fields.Datetime.to_string(
                        dateutil.parser.parse(default_tenant.get('deactivation'), tzinfos=tzinfos).astimezone(pytz.utc)),
                })
                tenant._switch()
            else:
                created_tenant = request.env["omna.tenant"].with_context({'synchronizing': True}).create({
                    'omna_tenant_id': default_tenant.get('id'),
                    'name': default_tenant.get('name'),
                    'token': default_tenant.get('token'),
                    'secret': default_tenant.get('secret'),
                    'is_ready_to_omna': default_tenant.get('is_ready_to_omna'),
                    'deactivation': odoo.fields.Datetime.to_string(
                        dateutil.parser.parse(default_tenant.get('deactivation'), tzinfos=tzinfos).astimezone(pytz.utc)),
                    # 'current': True
                })
                request.env.user.context_omna_current_tenant = created_tenant
            return True

        return False

    @http.route('/omna/integrations/authorize/<string:integration_id>', type='http', auth='user', methods=['GET'])
    def authorize_integration(self, integration_id, **kw):
        integration = request.env['omna.integration'].search([('integration_id', '=', integration_id)], limit=1)
        channel_value = integration.channel
        if integration:
            integration.write({'authorized': True, 'channel': channel_value})
            # redirect = '/web#action=%s&model=omna.integration&view_type=kanban&menu_id=%s' % (request.env.ref('ecapi_mercado_libre.action_omna_integration').id, request.env.ref('ecapi_mercado_libre.menu_omna_my_integrations').id)
            # redirect = '/web#action=%s&cids=1&home=&menu_id=%s&model=omna.integration&view_type=kanban' % (request.env.ref('ecapi_mercado_libre.action_omna_integration').id, request.env.ref('ecapi_mercado_libre.menu_omna_my_integrations').id)
            # return werkzeug.utils.redirect(redirect)
            return werkzeug.utils.redirect('/web#action={0}'.format(request.env.ref('ecapi_mercado_libre.action_omna_integration').id))
            # return http.redirect_with_hash(redirect)
        else:
            raise exceptions.AccessError(_("Invalid integration id."))

    @http.route('/omna/options/service', type='json', auth='user', methods=['GET', 'POST'], csrf=False)
    def omna_options_service(self, path=None, term='', **kw):
        if path:
            data = request.env['omna.api'].get(path, {'term': term})
            return data
        else:
            return False

