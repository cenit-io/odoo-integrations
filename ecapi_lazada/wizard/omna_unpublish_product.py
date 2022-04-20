# -*- coding: utf-8 -*-

import logging, odoo
from datetime import datetime, timezone
import dateutil.parser
from odoo import models, api, exceptions, fields, _
import pytz

_logger = logging.getLogger(__name__)


class OmnaUnpublishProductWizard(models.TransientModel):
    _name = 'omna.unpublish_product_wzd'
    _inherit = 'omna.api'

    delete_from_integration = fields.Boolean(default=False)
    integration_ids = fields.Many2many('omna.integration', 'omna_unpublish_product_wzd_integration_rel', 'unpublish_product_id', 'integration_id', 'Integrations', required=True)


    def unpublish_product(self):
        try:
            product = self.env['product.template'].search([('id', '=', self._context.get('active_id'))])
            integrations = []
            for integration in self.integration_ids:
                integrations.append(integration.integration_id)
            data = {
                'data': {
                    'integration_ids': integrations,
                    'delete_from_integration': self.delete_from_integration
                }
            }
            result = self.patch('products/%s' % product.omna_product_id, data)

            return True
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)




