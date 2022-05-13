# -*- coding: utf-8 -*-

import requests
import base64
import json
import logging
from datetime import *
from odoo.exceptions import ValidationError
# from odoo import models, api, exceptions, fields
from odoo import models, fields, api, exceptions, tools, _

_logger = logging.getLogger(__name__)


class OmnaSyncProducts(models.TransientModel):
    _name = 'omna.sync_products_wizard'
    _inherit = 'omna.api'


    integration_id = fields.Many2one('omna.integration', 'Integration')




    def import_function(self):
        try:
            self.by_integration_import_products(self.integration_id.integration_id)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
        pass


    # Importacion

    def by_integration_import_products(self, param_integration_id):
        limit = 70
        offset = 0
        flag = True
        products = []
        create_list = []

        while flag:
            # response = self.get('integrations/%s/products' % (self.integration_id.integration_id,), {'limit': limit, 'offset': offset, 'with_details': True})
            response = self.get('integrations/%s/products' % (param_integration_id,), {'limit': limit, 'offset': offset})
            data = response.get('data')
            products.extend(data)
            if len(data) < limit:
                flag = False
            else:
                offset += limit

        product_obj = self.env['product.template']
        category_obj = self.env['product.category']

        for product in products:
            act_product = product_obj.search([('omna_product_id', '=', product.get('id'))])
            category_id = False
            categ_result = False

            category_or_brands = product.get('integration').get('product').get('properties', [])
            for cat_br in category_or_brands:
                if (cat_br.get('id') == 'category_id') and (cat_br.get('options')):
                    category_id = cat_br.get('value')

            categ_result = category_obj.search([('omna_category_id', '=', category_id)]) if category_id else False
            remote_product_id = product.get('integration').get('product').get('remote_product_id')
            if act_product:
                data = {
                    'name': product.get('name') or 'No definido',
                    'omna_product_id': product.get('id'),
                    'description': product.get('description') or 'No definido',
                    'list_price': product.get('price', 0),
                    'integrations_data': json.dumps(product.get('integration'), separators=(',', ':')),
                    'peso': product.get('package').get('weight', 0),
                    'alto': product.get('package').get('height', 0),
                    'longitud': product.get('package').get('length', 0),
                    'ancho': product.get('package').get('width', 0),
                    'overwrite': product.get('package').get('overwrite', False),
                    'omna_variant_qty': product.get('variants', 0),
                    'remote_product_id': remote_product_id,
                    'integration_ids': self.integration_id.id
                }
                if (len(product.get('images'))):
                    url = product.get('images')[0]
                    if url:
                        image = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
                        data['image_1920'] = image

                if len(product.get('integration', [])):
                    data.update({'state_integration': 'linked', 'marketplace_state': 'published' if 'PENDING-PUBLISH-FROM-' not in remote_product_id else 'unpublished'})

                    if categ_result:
                        data.update({'categ_id': categ_result.id})


                act_product.with_context(from_omna_api=True).write(data)

            else:
                data = {
                    'name': product.get('name') or 'No definido',
                    'omna_product_id': product.get('id'),
                    'description': product.get('description') or 'No definido',
                    'list_price': product.get('price', 0),
                    'integrations_data': json.dumps(product.get('integration'), separators=(',', ':')),
                    'peso': product.get('package').get('weight', 0),
                    'alto': product.get('package').get('height', 0),
                    'longitud': product.get('package').get('length', 0),
                    'ancho': product.get('package').get('width', 0),
                    'overwrite': product.get('package').get('overwrite', False),
                    'omna_variant_qty': product.get('variants', 0),
                    'remote_product_id': remote_product_id,
                    'integration_ids': self.integration_id.id
                }
                if len(product.get('images', [])):
                    url = product.get('images')[0]
                    if url:
                        image = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
                        data['image_1920'] = image

                if len(product.get('integration', [])):
                    data.update({'state_integration': 'linked', 'marketplace_state': 'published' if 'PENDING-PUBLISH-FROM-' not in remote_product_id else 'unpublished'})

                    if categ_result:
                        data.update({'categ_id': categ_result.id})

                # act_product = product_obj.with_context(synchronizing=True).create(data)
                create_list.append(data)

        product_obj.with_context(from_omna_api=True).create(create_list)
        self.env.cr.commit()
        self.env.user.notify_channel('info', _('The process for import products have been finished.'), _("Information"), True)

