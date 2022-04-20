# -*- coding: utf-8 -*-

import requests
import base64
import json
import logging
import re
from datetime import datetime, timezone, time
from odoo.exceptions import ValidationError
from odoo import models, api, exceptions, fields

_logger = logging.getLogger(__name__)


class OmnaExtraImport(models.TransientModel):
    _name = 'omna.extra.import'
    _inherit = 'omna.api'



    integration_id = fields.Many2one('omna.integration', 'Integration')
    function_selection = fields.Selection(
        [('import_attributes_values', 'Attributes / Values'), ('import_stock_warehouse', 'Stock Warehouse'),
         ('import_stock_items', 'Stock Items'), ('import_tax_rules', 'Tax Rules'),
         ('import_carriers', 'Carriers')], string='Operation')




    def execute_function(self):
        if self.function_selection == "import_attributes_values":
            self.import_attributes_values()
        if self.function_selection == "import_stock_warehouse":
            self.import_stock_warehouse()
        if self.function_selection == "import_stock_items":
            self.import_stock_items()
        if self.function_selection == "import_tax_rules":
            self.import_tax_rules()
        if self.function_selection == "import_carriers":
            self.import_carriers()

        # form_view_id = self.env.ref('ecapi_lazada.view_omna_extra_import_wizard').id

        # return {'type': 'ir.actions.act_window_close'}



    def import_attributes_values(self):
        limit = 20
        offset = 0
        flag = True
        products = []

        while flag:
            response = self.get('integrations/%s/products' % (self.integration_id.integration_id, ), {'limit': limit, 'offset': offset})
            data = response.get('data')
            match_data = [x for x in response.get('data') if x.get('variants') >= 1]
            products.extend(match_data)
            if match_data or (len(data) < limit):
                flag = False
            else:
                offset += limit

        if products:
            response_variant = self.get('products/%s/variants' % products[0].get('id'), {'limit': 5, 'offset': 0, 'with_details': True})
            remote_result = response_variant.get('data')
            attributes_list = remote_result[0].get('integrations')[0].get('variant').get('properties')
            product_attribute_obj = self.env['product.attribute']
            aux_list = []

            for item in attributes_list:
                value_collection = []
                if item.get('input_type') == "single_select":
                    lolo = {frozenset(X.items()): X for X in [{'omna_attribute_value_id': res.get('value', -1) or -1,
                                                               'name': res.get('label', "-") or "-"} for res in
                                                              item.get('options')]}.values()
                    b = [(0, 0, Y) for Y in lolo]
                    value_collection.extend(b)


                    aux_list.append({'name': item.get('label'),
                                 'omna_attribute_id': item.get('id'),
                                 'value_ids': value_collection})

            product_attribute_obj.create(aux_list)
            self.env.cr.commit()

            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }

        else:
            self.env.user.notify_channel('danger',
                'The import process for attributes from Prestashop is not possible.\n'
                ' Please verify that you have products with variants or combinations created previously.',
                                         "Error", True)

        # # https://cenit.io/app/ecapi-v1/integrations/prestashop_col10/call/native/service
        # data_aux1 = {"data": {"path": "/product_features",
        #                      "method": "GET",
        #                      "params": {"display": "full"}}}
        # data_aux2 = {"data": {"path": "/product_feature_values",
        #                      "method": "GET",
        #                      "params": {"display": "full"}}}
        # response1 = self.post('integrations/%s/call/native/service' % (self.integration_id.integration_id,), data_aux1)
        # response2 = self.post('integrations/%s/call/native/service' % (self.integration_id.integration_id,), data_aux2)
        #
        # attributes_list = response1.get('data').get('product_features')
        # values_list = response2.get('data').get('product_feature_values')
        # product_attribute_obj = self.env['product.attribute']
        # records_list = []
        # for item in attributes_list:
        #     values_temp = list(filter(lambda d: d.get('id_feature') == str(item.get('id')), values_list))
        #     # records_list.append()
        #     lolo = {'name': item.get('name'),
        #      'omna_attribute_id': str(item.get('id')),
        #      'value_ids': [(0, 0, {'omna_attribute_value_id': str(X.get('id')), 'name': X.get('value')}) for X in values_temp]}
        #
        #     product_attribute_obj.create(lolo)
        #     self.env.cr.commit()
        #
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'reload'
        # }
    
    
    def import_stock_warehouse(self):
        # Agregar la creación de un almacén físico asociado a la locación importada desde Omna.
        limit = 20
        offset = 0
        flag = True
        locations = []

        while flag:
            # https://cenit.io/app/ecapi-v1/integrations/{integration_id}/stock/locations
            response = self.get('integrations/%s/stock/locations' % (self.integration_id.integration_id), {'limit': limit, 'offset': offset})
            data = response.get('data')
            # match_data = [x for x in response.get('data') if x.get('variants') >= 1]
            # products.extend(match_data)
            locations.extend(data)
            # if match_data or (len(data) < limit):
            if len(data) < limit:
                flag = False
            else:
                offset += limit

        stock_warehouse_obj = self.env['stock.warehouse']
        aux_list = []
        query_items = stock_warehouse_obj.search([('omna_id', '!=', False)]).mapped('omna_id')
        result = [X for X in locations if X.get('id') not in query_items]

        for location in result:
            data = {
                'name': location.get('name'),
                'code': location.get('name'),
                'omna_id': location.get('id'),
                'integration_id': self.integration_id.id,

            }

            aux_list.append(data)

        stock_warehouse_obj.create(aux_list)
        self.env.cr.commit()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }

        # else:
        #     self.env.user.notify_channel('danger',
        #                                  'The import process for stock warehouse from Prestashop is not possible.\n'
        #                                  ' Please verify your access data.',
        #                                  "Error", True)
    
    
    def import_stock_items(self):
        limit = 50
        offset = 0
        flag = True
        stock_items = []

        while flag:
        # if flag:
            # https://cenit.io/app/ecapi-v1/stock/items
            response = self.get('stock/items', {'limit': limit, 'offset': offset, 'integration_id': self.integration_id.integration_id})
            data = response.get('data')

            filtered = filter(lambda item: item.get('count_on_hand') > 0, data)
            stock_items.extend(list(filtered))

            # stock_items.extend(data)
            if len(data) < limit:
                flag = False
            else:
                offset += limit

        stock_items_obj = self.env['omna.stock.items']
        aux_list = []
        query_items = stock_items_obj.search([]).mapped('omna_id')
        stock_location_id = self.env['stock.location'].search([('omna_id', '!=', False)])
        result = [X for X in stock_items if X.get('id') not in query_items]

        for item in result:
            # product_product_id = self.env['product.product'].search([('omna_variant_id', '=', item.get('product').get('variant').get('id'))])
            # if product_product_id and stock_location_id:

            # product_template_id = self.env['product.template'].search([('omna_product_id', '=', item.get('product').get('id'))])
            # # product_product_id = self.env['product.product'].search([('product_tmpl_id', '=', product_template_id.id)])
            # data = {
            #     'omna_id': item.get('id', False),
            #     'integration_id': self.integration_id.id,
            #     'product_template_id': product_template_id.id,
            #     'stock_location_id': stock_location_id.id,
            #     'count_on_hand': item.get('count_on_hand', 0),
            # }

            data = {
                'omna_id': item.get('id', False),
                'integration_id': self.integration_id.id,
                'stock_location_id': stock_location_id.id,
                'product_product_name': "%s [%s]" % (item.get('product').get('name'), item.get('product').get('variant').get('sku')),
                'product_template_name': item.get('product').get('name'),
                'product_product_omna_id': item.get('product').get('variant').get('id'),
                'product_template_omna_id': item.get('product').get('id'),
                'count_on_hand': item.get('count_on_hand', 0),
            }

            aux_list.append(data)

        stock_items_obj.create(aux_list)
        self.env.cr.commit()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }


    def extract_percent(self, text_value):
        if text_value.count('%') > 0:
            result = re.findall(r'[\d\.\d]+', text_value)
            if result[0].count('.') == 0:
                return int(result[0])
            if result[0].count('.') == 1:
                return float(result[0])
        else:
            return 18


    def import_tax_rules(self):
        limit = 5
        offset = 0
        flag = True
        products = []

        response = self.get('integrations/%s/products' % (self.integration_id.integration_id, ), {'limit': limit, 'offset': offset, 'with_details': True})
        data = response.get('data')
        products.extend(data)

        if products:
            # response_variant = self.get('products/%s/variants' % products[0].get('id'), {'limit': 5, 'offset': 0, 'with_details': True})
            # remote_result = response_variant.get('data')
            properties_list = products[0].get('integration').get('product').get('properties')
            account_tax_obj = self.env['account.tax']
            aux_list = []

            for item in properties_list:
                value_collection = []
                if item.get('id') == "id_tax_rules_group":
                    item.get('options')
                    aux_list.extend([{'name': X.get('label'),
                                     'description': X.get('label'),
                                     'omna_tax_rule_id': X.get('value'),
                                     'integration_id': self.integration_id.id,
                                     'amount': self.extract_percent(X.get('label'))} for X in item.get('options') if X.get('label') != '-'])

            account_tax_obj.create(aux_list)
            self.env.cr.commit()

            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }

        else:
            self.env.user.notify_channel('danger',
                'The import process for attributes from Prestashop is not possible.\n'
                ' Please verify that you have products with variants or combinations created previously.',
                                         "Error", True)


    def import_carriers(self):
        carriers = []

        # https://cenit.io/app/ecapi-v1/integrations/prestashop_col10/call/native/service
        data = {"data": {"path": "/carriers", "method": "GET", "params": {"display": "full", "limit": "0,100", "filter[deleted]": "0"}}}
        response = self.post('integrations/%s/call/native/service' % (self.integration_id.integration_id, ), data)
        carriers.extend(response.get('data').get('carriers'))

        product_obj = self.env['product.template']
        aux_list = []

        for item in carriers:
            act_product = product_obj.search([('type', '=', 'service'), ('omna_product_id', '=', item.get('id'))])

            if act_product:
                data = {
                    'name': item.get('name') or 'No definido',
                    'type': "service",
                    'omna_product_id': item.get('id'),
                    'default_code': item.get('id_reference'),
                    'description': item.get('delay') or 'No definido',
                    'list_price': 0,
                    'taxes_id': False
                }

                act_product.with_context(synchronizing=True).write(data)

            else:
                data = {
                    'name': item.get('name') or 'No definido',
                    'type': "service",
                    'omna_product_id': item.get('id'),
                    'default_code': item.get('id_reference'),
                    'description': item.get('delay') or 'No definido',
                    'list_price': 0,
                    'taxes_id': False
                }

                aux = []
                aux.append((0, 0, {'integration_ids': self.integration_id.id,
                                   'remote_product_id': item.get('id'),
                                   'delete_from_integration': False}))
                data['integration_ids'] = aux

                aux_list.append(data)

        product_obj.with_context(synchronizing=True).create(aux_list)
        self.env.cr.commit()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }
