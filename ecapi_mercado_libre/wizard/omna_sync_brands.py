# -*- coding: utf-8 -*-

import requests
import base64
import json
import logging
import hmac
import hashlib
from datetime import datetime, timezone, time
from odoo import models, api, exceptions, fields


_logger = logging.getLogger(__name__)


class OmnaSyncBrands(models.TransientModel):
    _name = 'omna.sync_brands_wizard'
    _inherit = 'omna.api'

    sync_type = fields.Selection([('by_integration', 'By Integration'),
                                  ('by_external_id', 'By External Id')], 'Import Type',
                                 required=True, default='by_integration')
    integration_id = fields.Many2one('omna.integration', 'Integration', domain=lambda self:[('company_id', '=', self.env.company.id)])
    brand_id = fields.Many2one('product.brand', 'Brand')
    quantity_max = fields.Integer('Max Quantity', default=100)

    def sync_brands(self):
        try:
            limit = 50
            offset = 0
            requester = True
            brands = []

            if self.sync_type == 'by_integration':
                while requester:
                    response = self.get('integrations/%s/brands' % self.integration_id.integration_id, {'limit': limit, 'offset': offset, 'with_details': 'true'})
                    data = response.get('data')
                    brands.extend(data)
                    offset += limit
                    if (len(data) < limit) or (offset == self.quantity_max):
                        requester = False

            else:
                external = self.brand_id.omna_brand_id
                if external:
                    response = self.get(
                        'integrations/%s/brands/%s' % (self.integration_id.integration_id, external),
                        {})
                data = response.get('data')
                brands.append(data)


            brand_obj = self.env['product.brand']
            for brand in brands:
                act_brand = brand_obj.search([('omna_brand_id', '=', brand.get('id'))])
                if act_brand:
                    # name = brand.get('name')
                    data = {
                        'name': brand.get('name'),
                    }
                    act_brand.with_context(synchronizing=True).write(data)
                else:
                    # name = brand.get('name').split('>')
                    # parent_id = brand_obj.search([('name', '=', name[len(name)-2])], limit=1)
                    data = {
                        'name': brand.get('name'),
                        'omna_brand_id': brand.get('id'),
                        'integration_id': self.integration_id.id
                    }
                    act_brand = brand_obj.with_context(synchronizing=True).create(data)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)


