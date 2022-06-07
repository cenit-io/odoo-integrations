# -*- coding: utf-8 -*-

import requests
import base64
import json
import logging
import hmac
import hashlib
from datetime import datetime, timezone, time
from odoo import models, api, exceptions


_logger = logging.getLogger(__name__)


class OmnaSyncIntegrations(models.TransientModel):
    _name = 'omna.sync_integrations_wizard'
    _inherit = 'omna.api'

    def sync_integrations(self):
        try:
            limit = 25
            offset = 0
            requester = True
            integrations = []
            while requester:
                response = self.get('integrations', {'limit': limit, 'offset': offset, 'with_details': 'true'})
                data = list(filter(lambda d: 'MercadoLibre' in d['channel'], response.get('data')))
                integrations.extend(data)
                if len(data) < limit:
                    requester = False
                else:
                    offset += limit

            integration_obj = self.env['omna.integration']
            for integration in integrations:
                act_integration = integration_obj.search([('integration_id', '=', integration.get('id')), ('omna_tenant_id', '=', self.env.user.context_omna_current_tenant.id)])
                if act_integration:
                    data = {
                        'name': integration.get('name'),
                        'channel': integration.get('channel'),
                        'authorized': integration.get('authorized')
                    }
                    act_integration.with_context(synchronizing=True).write(data)
                else:
                    data = {
                        'name': integration.get('name'),
                        'integration_id': integration.get('id'),
                        'channel': integration.get('channel'),
                        'authorized': integration.get('authorized')
                    }
                    act_integration = integration_obj.with_context(synchronizing=True).create(data)
            self.env.cr.commit()
            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)


