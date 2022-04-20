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

    sync_type = fields.Selection([('by_integration', 'By Integration'), ('by_omna_id', 'By Omna ID')], 'Operation Critery', required=True, default='by_integration')
    integration_id = fields.Many2one('omna.integration', 'Integration')
    omna_id = fields.Char('Product OMNA ID')
    product_sku = fields.Char('Product SKU')


    @api.onchange('sync_type')
    def _onchange_sync_type(self):
        self.integration_id = False
        self.omna_id = False
        self.product_sku = False


    def import_function(self):
        try:
            if self.sync_type == 'by_integration':
                # record_id = self.env.ref('ecapi_lazada.by_integration_import_products_cron').id
                # data = {'active': True,
                #         'nextcall': (datetime.now() + timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S'),
                #         'user_id': self.env.uid,
                #         'code': "model.by_integration_import_products('{0}')".format(self.integration_id.integration_id)}
                # self.env['ir.cron'].browse(record_id).write(data)
                self.by_integration_import_products(self.integration_id.integration_id)
            if self.sync_type == 'by_omna_id':
                # record_id = self.env.ref('ecapi_lazada.by_omna_id_import_products_cron').id
                # data = {'active': True,
                #         'nextcall': (datetime.now() + timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S'),
                #         'user_id': self.env.uid,
                #         'code': "model.by_omna_id_import_products('{0}','{1}')".format(self.integration_id.integration_id, self.omna_id)}
                # self.env['ir.cron'].browse(record_id).write(data)
                self.by_omna_id_import_products(self.integration_id.integration_id, self.omna_id)
            # if self.sync_type == 'by_product_sku':
            #     record_id = self.env.ref('ecapi_lazada.by_product_sku_import_products_cron').id
            #     data = {'active': True,
            #             'nextcall': (datetime.now() + timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S'),
            #             'user_id': self.env.uid,
            #             'code': "model.by_product_sku_import_products('{0}','{1}')".format(self.integration_id.integration_id, self.product_sku)}
            #     self.env['ir.cron'].browse(record_id).write(data)
            #     # self.by_product_sku_import_products()

            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
        pass


    # Importacion

    def by_integration_import_products(self, integration_id):
        limit = 70
        offset = 0
        flag = True
        products = []
        create_list = []

        while flag:
            # response = self.get('integrations/%s/products' % (self.integration_id.integration_id,), {'limit': limit, 'offset': offset, 'with_details': True})
            response = self.get('integrations/%s/products' % (integration_id,), {'limit': limit, 'offset': offset})
            data = response.get('data')
            filtered = filter(lambda item: item.get('quantity', 0) > 0, data)
            products.extend(list(filtered))
            # products.extend(data)
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
                    'omna_variant_qty': product.get('variants', 0)
                }
                if (len(product.get('images'))):
                    url = product.get('images')[0]
                    if url:
                        image = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
                        data['image_1920'] = image

                if len(product.get('integration', [])):
                    integrations = []
                    aux = []
                    new_linked = False
                    integration = product.get('integration', False)
                    if integration:
                        integrations.append(integration.get('id'))
                        integration_id = self.env['omna.integration'].search([('integration_id', '=', integration.get('id'))])
                        linked = next((i for i in act_product.integration_ids if
                                       i.integration_ids.integration_id == integration.get('id')), False)
                        if not linked:
                            aux.append((0, 0, {'integration_ids': integration_id.id,
                                               'remote_product_id': integration.get('product').get('remote_product_id'),
                                               'delete_from_integration': True}))
                            new_linked = True

                    if categ_result:
                        data.update({'categ_id': categ_result.id})

                    omna_integration = self.env['omna.integration'].search([('integration_id', 'in', integrations)])
                    data['integration_linked_ids'] = [(6, 0, omna_integration.ids)]
                    data['integration_ids'] = aux if new_linked else []

                act_product.with_context(from_omna_api=True).write(data)

            else:
                data = {
                    'name': product.get('name') or 'No definido',
                    'omna_product_id': product.get('id'),
                    'description': product.get('description') or 'No definido',
                    'list_price': product.get('price', 0),
                    'integrations_data': json.dumps(product.get('integrations'), separators=(',', ':')),
                    'peso': product.get('package').get('weight', 0),
                    'alto': product.get('package').get('height', 0),
                    'longitud': product.get('package').get('length', 0),
                    'ancho': product.get('package').get('width', 0),
                    'overwrite': product.get('package').get('overwrite', False),
                    'omna_variant_qty': product.get('variants', 0)
                }
                if len(product.get('images', [])):
                    url = product.get('images')[0]
                    if url:
                        image = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
                        data['image_1920'] = image

                if len(product.get('integration', [])):
                    integrations = []
                    aux = []
                    integration = product.get('integration', False)
                    if integration:
                        integrations.append(integration.get('id'))
                        integration_id = self.env['omna.integration'].search([('integration_id', '=', integration.get('id'))])
                        aux.append((0, 0, {'integration_ids': integration_id.id,
                                           'remote_product_id': integration.get('product').get('remote_product_id'),
                                           'delete_from_integration': True}))

                    if categ_result:
                        data.update({'categ_id': categ_result.id})

                    omna_integration = self.env['omna.integration'].search([('integration_id', 'in', integrations)])
                    data['integration_linked_ids'] = [(6, 0, omna_integration.ids)]
                    data['integration_ids'] = aux

                # act_product = product_obj.with_context(synchronizing=True).create(data)
                create_list.append(data)

        product_obj.with_context(from_omna_api=True).create(create_list)
        self.env.cr.commit()
        self.env.user.notify_channel('info', _('The process for import products have been finished.'), _("Information"), True)


    def by_omna_id_import_products(self, integration_id, omna_id):
        product = None

        if omna_id:
            response = self.get('integrations/%s/products/%s' % (integration_id, omna_id), {'with_details': True})
            data = response.get('data')
            product = data
        else:
            raise ValidationError(('Product with ID: %s was not found in integration %s') % (omna_id, integration_id))

        product_obj = self.env['product.template']

        if product:
            act_product = product_obj.search([('omna_product_id', '=', product.get('id'))])
            category_id = False
            categ_result = False

            category_or_brands = product.get('integration').get('product').get('properties', [])
            for cat_br in category_or_brands:
                if (cat_br.get('id') == 'category_id') and (cat_br.get('options')):
                    category_id = cat_br.get('value')

            categ_result = self.env['product.category'].search([('omna_category_id', '=', category_id)])

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
                    'omna_variant_qty': product.get('variants', 0)
                }
                if (len(product.get('images'))):
                    url = product.get('images')[0]
                    if url:
                        image = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
                        data['image_1920'] = image

                if len(product.get('integration', [])):
                    integrations = []
                    aux = []
                    new_linked = False
                    integration = product.get('integration', False)
                    if integration:
                        integrations.append(integration.get('id'))
                        integration_id = self.env['omna.integration'].search(
                            [('integration_id', '=', integration.get('id'))])
                        linked = next((i for i in act_product.integration_ids if
                                       i.integration_ids.integration_id == integration.get('id')), False)
                        if not linked:
                            aux.append((0, 0, {'integration_ids': integration_id.id,
                                               'remote_product_id': integration.get('product').get('remote_product_id'),
                                               'delete_from_integration': True}))
                            new_linked = True


                    if categ_result:
                        data.update({'categ_id': categ_result.id})

                    omna_integration = self.env['omna.integration'].search([('integration_id', 'in', integrations)])
                    data['integration_linked_ids'] = [(6, 0, omna_integration.ids)]
                    data['integration_ids'] = aux if new_linked else []

                act_product.with_context(from_omna_api=True).write(data)

            else:
                data = {
                    'name': product.get('name') or 'No definido',
                    'omna_product_id': product.get('id'),
                    'description': product.get('description') or 'No definido',
                    'list_price': product.get('price', 0),
                    'integrations_data': json.dumps(product.get('integrations'), separators=(',', ':')),
                    'peso': product.get('package').get('weight', 0),
                    'alto': product.get('package').get('height', 0),
                    'longitud': product.get('package').get('length', 0),
                    'ancho': product.get('package').get('width', 0),
                    'overwrite': product.get('package').get('overwrite', False),
                    'omna_variant_qty': product.get('variants', 0)
                }
                if len(product.get('images', [])):
                    url = product.get('images')[0]
                    if url:
                        image = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
                        data['image_1920'] = image

                if len(product.get('integration', [])):
                    integrations = []
                    aux = []
                    integration = product.get('integration', False)
                    if integration:
                        integrations.append(integration.get('id'))
                        integration_id = self.env['omna.integration'].search(
                            [('integration_id', '=', integration.get('id'))])
                        aux.append((0, 0, {'integration_ids': integration_id.id,
                                           'remote_product_id': integration.get('product').get('remote_product_id'),
                                           'delete_from_integration': True}))

                    if categ_result:
                        data.update({'categ_id': categ_result.id})

                    omna_integration = self.env['omna.integration'].search([('integration_id', 'in', integrations)])
                    data['integration_linked_ids'] = [(6, 0, omna_integration.ids)]
                    data['integration_ids'] = aux

                product_obj.with_context(from_omna_api=True).create(data)

            self.env.cr.commit()
            self.env.user.notify_channel('info', _('The process for import products have been finished.'), _("Information"), True)

