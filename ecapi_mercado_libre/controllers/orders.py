# -*- coding: utf-8 -*-
from odoo import http, exceptions, SUPERUSER_ID
from odoo.http import request
import odoo
import logging
import json
import hmac
import hashlib
import werkzeug
import requests
import dateutil.parser
import pytz

_logger = logging.getLogger(__name__)


class OrdersController(http.Controller):

    @http.route('/omna/order', type='json', auth='none', methods=['POST'], csrf=False)
    def order(self, **kwargs):
        if self._check_sign():
            tenant = request.env['omna.tenant'].with_user(SUPERUSER_ID).search(
                [('token', '=', request.httprequest.headers.get('X-Tenant-Token'))])
            data = json.loads(request.httprequest.data)
            if data.get('data'):
                order = data.get('data')
                order['omna_tenant_id'] = tenant.id
                return request.env['omna.order.mixin'].with_user(SUPERUSER_ID).sync_orders([order])
        return False

    def _check_sign(self):
        tenant = request.env['omna.tenant'].with_user(SUPERUSER_ID).search([('token', '=', request.httprequest.headers.get('X-Tenant-Token'))])
        if tenant:
            hmac1 = request.httprequest.headers.get('X-HMac-Sha256')
            hmac2 = hmac.new(bytes(tenant.secret, 'utf-8'), msg=request.httprequest.data,
                             digestmod=hashlib.sha256).hexdigest()
            if hmac1 == hmac2:
                return True
        return False
