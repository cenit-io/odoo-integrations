# -*- coding: utf-8 -*-

import logging, odoo
from datetime import datetime, timezone
import dateutil.parser
from odoo import models, api, exceptions, fields, _
import pytz

_logger = logging.getLogger(__name__)


class OmnaPublishProductWizard(models.TransientModel):
    _name = 'omna.publish_product_wzd'
    _inherit = 'omna.api'

    product_id = fields.Many2one('product.template', 'Product')
    link_with_its_variants = fields.Selection([
        ('NONE', 'NONE'),
        ('SELECTED', 'SELECTED'),
        ('NEW', 'NEW'),
        ('ALL', 'ALL')], default='NONE', required=True)
    integration_ids = fields.Many2many('omna.integration', 'omna_publish_product_wzd_integration_rel', 'publish_product_id', 'integration_id', 'Integrations', required=True)


    def publish_product(self):
        publish = self.env['omna.publish_product_wzd'].search([('product_id', '=', self._context.get('active_id'))])
        if publish:
            raise exceptions.AccessError(_('This product is already published'))

        try:
            product = self.env['product.template'].search([('id', '=', self._context.get('active_id'))])
            integrations = []
            for integration in self.integration_ids:
                integrations.append(integration.integration_id)
            data = {
                'data': {
                    'integration_ids': integrations,
                    'link_with_its_variants': self.link_with_its_variants
                }
            }
            #result = self.put('products/%s' % product.omna_product_id, data)
            self.write({'product_id': product.id})
            return True
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)


    def unpublish_product(self):
        publish = self.env['omna.publish_product_wzd'].search([('product_id', '=', self._context.get('active_id'))])
        if not publish:
            raise exceptions.AccessError(_('This product is not published'))




