# -*- coding: utf-8 -*-

import logging, odoo
from datetime import datetime, timezone
import dateutil.parser
from odoo import models, api, exceptions, fields, _
import pytz

_logger = logging.getLogger(__name__)


class OmnaExportOrderWizard(models.TransientModel):
    _name = 'omna.export_order_wzd'
    _inherit = 'omna.api'

    integration_id = fields.Many2one('omna.integration', 'Integration')

    def export_order(self):
        try:
            order = self.env['sale.order'].search([('id', '=', self._context.get('active_id'))])
            data = {}
            if self.integration_id:
                data['target_integrarion_id'] = self.integration_id.integration_id
            result = self.put('orders/%s' % order.omna_id, {'data': data})

            self.env.user.notify_channel('warning', _(
                'The task to export the order have been created, please go to "System\Tasks" to check out the task status.'),
                                         _("Information"), True)
            return {'type': 'ir.actions.act_window_close'}

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)




