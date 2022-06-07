# -*- coding: utf-8 -*-

import logging, odoo
from datetime import datetime, timezone
import dateutil.parser
from odoo import models, api, exceptions, fields, _
import pytz

_logger = logging.getLogger(__name__)


class ActivateTenantWizard(models.TransientModel):
    _name = 'activate.tenant.wizard'
    _inherit = 'omna.api'

    @api.model
    def _current_tenant(self):
        current_tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)], limit=1)
        if current_tenant:
            return current_tenant.id
        else:
            return None

    omna_tenant_id = fields.Many2one('omna.tenant', 'Tenant', required=True, default=_current_tenant)



    def action_switch_tenant(self):
        try:
            tenant_obj = self.env['omna.tenant']
            tenant_obj.switch_action(self.omna_tenant_id.id)
        except Exception as e:
            _logger.error(e)
            raise exceptions.ValidationError(e)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload_context',
        }

