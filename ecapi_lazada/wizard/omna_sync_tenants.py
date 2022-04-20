# -*- coding: utf-8 -*-

import logging, odoo
from datetime import datetime, timezone
import dateutil.parser
from odoo import models, api, exceptions
import pytz

_logger = logging.getLogger(__name__)


class OmnaSyncTenants(models.TransientModel):
    _name = 'omna.sync_tenants_wizard'
    _inherit = 'omna.api'

    def sync_tenants(self):
        try:
            limit = 25
            offset = 0
            flag = True
            tenants = []
            tzinfos = {
                'PST': -8 * 3600,
                'PDT': -7 * 3600,
            }
            while flag:
                response = self.get('tenants', {'limit': limit, 'offset': offset})
                data = response.get('data')
                tenants.extend(data)
                if len(data) < limit:
                    flag = False
                else:
                    offset += limit

            for tenant in tenants:
                act_tenant = self.env['omna.tenant'].search([('omna_tenant_id', '=', tenant.get('id'))])
                if act_tenant:
                    # Updating the tenant
                    data = {
                        'name': tenant.get('name'),
                        'token': tenant.get('token'),
                        'secret': tenant.get('secret'),
                        'is_ready_to_omna': tenant.get('is_ready_to_omna'),
                        'deactivation': odoo.fields.Datetime.to_string(
                            dateutil.parser.parse(tenant.get('deactivation'), tzinfos=tzinfos).astimezone(pytz.utc)),
                    }
                    act_tenant.with_context(synchronizing=True).write(data)
                else:
                    data = {
                        'omna_tenant_id': tenant.get('id'),
                        'name': tenant.get('name'),
                        'token': tenant.get('token'),
                        'secret': tenant.get('secret'),
                        'is_ready_to_omna': tenant.get('is_ready_to_omna'),
                        'deactivation': odoo.fields.Datetime.to_string(
                            dateutil.parser.parse(tenant.get('deactivation'), tzinfos=tzinfos).astimezone(pytz.utc)),
                    }
                    act_tenant = self.env['omna.tenant'].with_context(synchronizing=True).create(data)

            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
