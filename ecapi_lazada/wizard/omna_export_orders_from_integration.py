# -*- coding: utf-8 -*-

import logging, odoo
from datetime import datetime, timezone
import dateutil.parser
from odoo import models, api, exceptions, fields, _
import pytz

_logger = logging.getLogger(__name__)


class OmnaExportOrdersFromIntegrationWizard(models.TransientModel):
    _name = 'omna.export_orders_from_integration_wzd'
    _inherit = 'omna.api'

    integration_id = fields.Many2one('omna.integration', 'From Integration',
                                     required=True)
    target_integration_id = fields.Many2one('omna.integration',
                                            'Target Integration',
                                            help='If the target_integrarion_id '
                                                 'parameter is omitted, the '
                                                 'order will be exported to '
                                                 'all integrations that have '
                                                 'the order export workflow '
                                                 'defined with its scheduler '
                                                 'disabled')

    def export_orders(self):
        try:
            # https://cenit.io/app/ecapi-v1/integrations/{integration_id}/orders
            order = self.env['sale.order'].search(
                [('id', '=', self._context.get('active_id'))])
            data = {}
            if self.target_integration_id:
                data[
                    'target_integration_id'] = self.target_integration_id.integration_id
            result = self.put(
                'integrations/%s/orders' % self.integration_id.integration_id,
                {'data': data})

            self.env.user.notify_channel('warning', _(
                'The task to export the updated orders been created, please go to "System\Tasks" to check out the task status.'),
                                         _("Information"), True)
            return {'type': 'ir.actions.act_window_close'}

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
