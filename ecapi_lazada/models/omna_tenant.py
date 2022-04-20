# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo
import datetime
from odoo import models, fields, api, exceptions, tools, _
import dateutil.parser
import pytz
import logging


_logger = logging.getLogger(__name__)


class OmnaTenant(models.Model):
    _name = 'omna.tenant'
    _inherit = 'omna.api'

    name = fields.Char('Name', required=True)
    omna_tenant_id = fields.Char('Tenant identifier in OMNA', index=True, readonly=True)
    token = fields.Char('Token', required=True, readonly=True)
    secret = fields.Char('Secret', required=True, readonly=True)
    is_ready_to_omna = fields.Boolean('Is ready to OMNA', readonly=True)
    deactivation = fields.Datetime('Deactivation', readonly=True)

    def _compute_current(self):
        for record in self:
            record.current = self.env.user.context_omna_current_tenant.id == record.id

    current = fields.Boolean('Current Tenant', default=False, invisible=True, compute=_compute_current, store=True)

    @api.model
    def create(self, vals_list):
        if not self._context.get('synchronizing'):
            data = {
                'name': vals_list['name']
            }
            response = self.post('tenants', {'data': data})
            tzinfos = {
                'PST': -8 * 3600,
                'PDT': -7 * 3600,
            }
            if response.get('data').get('id'):
                vals_list['omna_tenant_id'] = response.get('data').get('id')
                vals_list['token'] = response.get('data').get('token')
                vals_list['secret'] = response.get('data').get('secret')
                vals_list['is_ready_to_omna'] = response.get('data').get('is_ready_to_omna')
                vals_list['deactivation'] = odoo.fields.Datetime.to_string(
                    dateutil.parser.parse(response.get('data').get('deactivation'), tzinfos=tzinfos).astimezone(
                        pytz.utc))
                return super(OmnaTenant, self).create(vals_list)
            else:
                raise exceptions.AccessError(_("Error trying to push tenant to Omna's API."))
        else:
            return super(OmnaTenant, self).create(vals_list)

    def unlink(self):
        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        for rec in self:
            response = rec.delete('tenants/%s' % rec.omna_tenant_id)
        return super(OmnaTenant, self).unlink()

    @api.model
    def _switch(self):
        self.ensure_one()
        self.env.user.context_omna_current_tenant = self.id
        return True

    def switch(self):
        self._switch()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }

    @api.model
    def switch_action(self, id):
        tenant = self.browse(id)
        if tenant:
            return tenant._switch()
        else:
            return False