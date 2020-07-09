# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)
try:
    import inflect
except ImportError as err:
    _logger.debug(err)

from odoo import http
from odoo.http import request
import json


class ShipstationWebhookController(http.Controller):
    @http.route('/ship/notify', type='json', auth='public',
                methods=['POST'], csrf=False)
    def ship_notify(self, **post):
        webhook_payload = json.loads(request.httprequest.data)
        _logger.info(webhook_payload)
        url = webhook_payload['resource_url']
        json_data = request.env['shipstation.api'].get(url)
        request.env['sale.order'].sync_orders(json_data)
        return True


