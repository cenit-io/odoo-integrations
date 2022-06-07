# -*- coding: utf-8 -*-

import logging, odoo
from datetime import datetime, timezone
import dateutil.parser
from odoo import models, api, exceptions, fields, _
import pytz

_logger = logging.getLogger(__name__)


class OmnaImportResourcesWizard(models.TransientModel):
    _name = 'omna.import_resources_wzd'
    _inherit = 'omna.api'

    resource = fields.Selection(
        [('products', 'Products'), ('orders', 'Orders'), ('brands', 'Brands'), ('categories', 'Categories')],
        'Resource', required=True)

    def import_resources(self):
        try:
            integration = self.env['omna.integration'].search([('id', '=', self._context.get('active_id'))])
            result = self.get('integrations/%s/%s/import' % (integration.integration_id, self.resource), {})

            self.env.user.notify_channel('warning', _(
                'The task to import the resources have been created, please go to "System\Tasks" to check out the task status.'),
                                         _("Information"), True)
            return {'type': 'ir.actions.act_window_close'}

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
