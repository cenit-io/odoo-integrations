# -*- coding: utf-8 -*-

import logging, odoo
from datetime import datetime, timezone
import dateutil.parser
from odoo import models, api, exceptions, fields, _
import pytz

_logger = logging.getLogger(__name__)


class OmnaReimportOrderWizard(models.TransientModel):
    _name = 'omna.reimport_order_wzd'
    _inherit = 'omna.api'

    def reimport_order(self):
        try:
            order = self.env['sale.order'].search([('id', '=', self._context.get('active_id'))])
            result = self.patch('orders/%s' % order.omna_id, {})

            self.env.user.notify_channel('warning', _(
                'The task to reimport the order have been created, please go to "System\Tasks" to check out the task status.'),
                                         _("Information"), True)
            return {'type': 'ir.actions.act_window_close'}

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)




