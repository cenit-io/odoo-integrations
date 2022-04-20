# -*- coding: utf-8 -*-
from odoo import models, api, _, fields, exceptions
from odoo.exceptions import UserError
import logging
import string
import random
import math

_logger = logging.getLogger(__name__)


def truncate(numero, cifras):
    posiciones = pow(10.0, cifras)
    return math.trunc(posiciones * numero) / posiciones



class OmnaMassiveVariantOpt(models.TransientModel):
    _name = "omna.massive.variant.opt"
    _inherit = 'omna.api'
    _description = "Omna Massive Variant Operations"

    integration_id = fields.Many2one('omna.integration', 'Integration')
    function_selection = fields.Selection(
        [('create_variants', 'Create Variants'), ('link_variants', 'Link Variants'),
         ('unlink_variants', 'Unlink Variants'), ('update_variants', 'Update Variants')], string='Operation')



    def execute_function(self):
        if self.function_selection == "create_variants":
            self.create_variants()
        if self.function_selection == "link_variants":
            self.link_variants()
        if self.function_selection == "unlink_variants":
            self.unlink_variants()
        if self.function_selection == "update_variants":
            self.update_variants()

        return {'type': 'ir.actions.act_window_close'}


    def create_variants(self):
        result_list = self.env['product.product'].search([('id', 'in', self._context.get('active_ids'))])
        for item in result_list:
            new_price = 0
            if item.product_tmpl_id.taxes_id.price_include:
                aux_price = item.product_tmpl_id.omna_tax_id.amount + 100
                to_round = item.product_tmpl_id.list_price / (aux_price / 100)
                formatted_string = str(truncate(to_round, 6))
                new_price = round(to_round, 5) if int(formatted_string[-1]) <= 5 else round(to_round, 6)

            if not item.product_tmpl_id.taxes_id.price_include:
                new_price = item.product_tmpl_id.list_price

            data = {
                'sku': item.default_code,
                'price': item.price_extra + new_price,
                'package': {'weight': item.peso, 'height': item.alto,
                            'length': item.longitud,
                            'width': item.ancho, 'content': "No definido"}
            }

            # https://cenit.io/app/ecapi-v1/products/{product_id}/variants
            response = self.post('products/%s/variants' % item.product_tmpl_id.omna_product_id, {'data': data})
            if response.get('data').get('id'):
                item.with_context(synchronizing=True).write({'omna_variant_id': response.get('data').get('id')})
            else:
                raise exceptions.AccessError(_("Error trying to push variant to Omna's API."))

        self.env.cr.commit()


    def link_variants(self):
        try:
            result_list = self.env['product.product'].search([('id', 'in', self._context.get('active_ids'))])
            all_values = [X.product_tmpl_id.omna_product_id for X in result_list]
            unique_values = set(all_values)
            for item in unique_values:
                parameters = {
                    "data": {
                        "variant_ids": [Y.omna_variant_id for Y in result_list if Y.product_tmpl_id.omna_product_id == item],
                        "integration_ids": [self.integration_id.integration_id]
                    }
                }
                # https://cenit.io/app/ecapi-v1/products/{product_id}/variants/link
                response = self.put('products/%s/variants/link' % item, parameters)

            for item in result_list:
                aux = []
                data = {}
                aux.append((0, 0, {'integration_ids': self.integration_id.id,
                                   'remote_variant_id': "PENDING-PUBLISH-FROM-" + item.omna_variant_id,
                                   'delete_from_integration': True}))
                data['integration_linked_ids'] = [(6, 0, self.integration_id.ids)]
                data['integration_ids'] = aux
                item.with_context(synchronizing=True).write(data)

            self.env.cr.commit()
            self.env.user.notify_channel('info',
                                         'Por favor revise el resultado de la tarea en Ebanux u Odoo.',
                                         u"Información", True)
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
        pass


    def unlink_variants(self):
        try:
            result_list = self.env['product.product'].search([('id', 'in', self._context.get('active_ids'))])
            all_values = [X.product_tmpl_id.omna_product_id for X in result_list]
            unique_values = set(all_values)
            for item in unique_values:
                parameters = {
                    "data": {
                        "variant_ids": [Y.omna_variant_id for Y in result_list if Y.product_tmpl_id.omna_product_id == item],
                        "integration_ids": [self.integration_id.integration_id],
                        "delete_from_integration": False
                    }
                }
                # https://cenit.io/app/ecapi-v1/products/{product_id}/variants/link
                response = self.delete('products/%s/variants/link' % item, parameters)

            for item in result_list:
                item.with_context(synchronizing=True).write({'integration_linked_ids': [(3, self.integration_id.id)]})

            self.env.cr.commit()
            self.env.user.notify_channel('info',
                                         'Por favor revise el resultado de la tarea en Ebanux u Odoo.',
                                         u"Información", True)
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
        pass



    def update_variants(self):
        variant_list = self.env['product.product'].search([('id', 'in', self._context.get('active_ids'))])
        all_values = [X.product_tmpl_id.omna_product_id for X in variant_list]
        unique_values = set(all_values)
        query_list = []
        for omna_product_id in unique_values:
            query1 = []
            for item in variant_list:
                if item.product_tmpl_id.omna_product_id == omna_product_id:
                    new_price = 0

                    if item.product_tmpl_id.taxes_id.price_include:
                        aux_price = item.product_tmpl_id.omna_tax_id.amount + 100
                        to_round = item.product_tmpl_id.list_price / (aux_price / 100)
                        formatted_string = str(truncate(to_round, 6))
                        new_price = round(to_round, 5) if int(formatted_string[-1]) <= 5 else round(to_round, 6)

                    if not item.product_tmpl_id.taxes_id.price_include:
                        new_price = item.product_tmpl_id.list_price

                    data = {
                        'variant_id': item.omna_variant_id,
                        'sku': item.default_code,
                        'price': item.price_extra + new_price,
                        # 'price': item.price_extra,
                        'package': {'weight': item.peso,
                                    'height': item.alto,
                                    'length': item.longitud,
                                    'width': item.ancho,
                                    'content': "No definido"
                                    }
                    }

                    query1.append(data)

            response1 = self.put('products/%s/variants' % (omna_product_id,), {'data': query1})
            if not (response1.get('data') and response1.get('type') == 'variant'):
                raise exceptions.AccessError(_("Error trying to update product variant in Omna's API."))

        for omna_product_id in unique_values:
            query2 = []
            for item in variant_list:
                if item.product_tmpl_id.omna_product_id == omna_product_id:
                    data2 = {
                        "variant_id": item.omna_variant_id,
                        "properties": [{"id": int(item2.attribute_id.omna_attribute_id),
                                        "value": int(item2.product_attribute_value_id.omna_attribute_value_id)} for
                                       item2 in
                                       item.product_template_attribute_value_ids]
                    }

                    query2.append(data2)

            response2 = self.post('integrations/%s/products/%s/variants' % (self.integration_id.integration_id, omna_product_id,), {"data": query2})
            query_list.extend(response2.get('data'))
            if not (response2.get('data') and response2.get('type') == 'di_variant'):
                raise exceptions.AccessError(_("Error trying to update product variant in Omna's API."))

        stock_list = []
        stock_location_id = self.env['stock.location'].search([('integration_id', '=', self.integration_id.id)])
        for query_item in query_list:
            # https://cenit.io/app/ecapi-v1/products/{product_id}/variants/{variant_id}/stock/items
            stock_result = self.get('products/%s/variants/%s/stock/items' % (query_item.get('product').get('id'), query_item.get('id')))
            stock_result = stock_result.get('data')[0]
            stock_data = {
                'omna_id': stock_result.get('id', False),
                'integration_id': self.integration_id.id,
                'stock_location_id': stock_location_id.id,
                'product_product_name': "[%s]" % query_item.get('product').get('name'),
                'product_template_name': query_item.get('product').get('name'),
                'product_product_omna_id': query_item.get('id'),
                'product_template_omna_id': query_item.get('product').get('id'),
                'count_on_hand': stock_result.get('count_on_hand', 0),
            }
            stock_list.append(stock_data)

        self.env['omna.stock.items'].create(stock_list)
        self.env.cr.commit()

