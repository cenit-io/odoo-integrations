# -*- coding: utf-8 -*-
from odoo import models, api, _, fields, exceptions
from odoo.exceptions import UserError
import logging
import math

_logger = logging.getLogger(__name__)

def truncate(numero, cifras):
    posiciones = pow(10.0, cifras)
    return math.trunc(posiciones * numero) / posiciones



class OmnaMassiveProductOpt(models.TransientModel):
    _name = "omna.massive.product.opt"
    _inherit = 'omna.api'
    _description = "Omna Massive Product Operations"

    integration_id = fields.Many2one('omna.integration', 'Integration', domain=lambda self:[('company_id', '=', self.env.company.id)])
    function_selection = fields.Selection(
        [('create_products', 'Create Products'), ('link_products', 'Link Products'),
         ('unlink_products', 'Unlink Products'), ('update_products', 'Update Products'),
         ('publish_products', 'Publish Products')], string='Operation')



    def execute_function(self):
        # if self.function_selection == "create_products":
        #     self.create_products()
        # if self.function_selection == "link_products":
        #     self.link_products()
        # if self.function_selection == "unlink_products":
        #     self.unlink_products()
        # if self.function_selection == "update_products":
        #     self.update_products()
        # if self.function_selection == "publish_products":
        #     self.publish_products()

        return {'type': 'ir.actions.act_window_close'}


    def create_products(self):
        result_list = self.env['product.template'].search([('id', 'in', self._context.get('active_ids'))])
        for item in result_list:

            new_price = 0

            if item.taxes_id.price_include:
                aux_price = item.omna_tax_id.amount + 100
                to_round = item.list_price / (aux_price / 100)
                formatted_string = str(truncate(to_round, 6))
                new_price = round(to_round, 5) if int(formatted_string[-1]) <= 5 else round(to_round, 6)
            if not item.taxes_id.price_include:
                new_price = item.list_price

            data = {
                'name': item.name,
                'price': new_price,
                'description': item.description,
                'package': {'weight': item.peso, 'height': item.alto,
                            'length': item.longitud,
                            'width': item.ancho, 'content': "No definido"}
            }

            response = self.post('products', {'data': data})
            if response.get('data').get('id'):
                item.with_context(synchronizing=True).write({'omna_product_id': response.get('data').get('id')})
            else:
                raise exceptions.AccessError(_("Error trying to push product to Omna's API."))

        self.env.cr.commit()
        self.env.user.notify_channel('info',
                                     'Por favor revise el resultado de la tarea en Ebanux u Odoo.',
                                     u"Información", True)


    def link_products(self):
        try:
            result_list = self.env['product.template'].search([('id', 'in', self._context.get('active_ids'))])
            parameters = {
                "data": {
                    "product_ids": result_list.mapped('omna_product_id'),
                    "integration_ids": [self.integration_id.integration_id],
                    "link_with_its_variants": "NONE"
                }
            }

            temp_result = self.put('products/link', parameters)

            for item in result_list:
                aux = []
                data = {}
                aux.append((0, 0, {'integration_ids': self.integration_id.id,
                                   'remote_product_id': "PENDING-PUBLISH-FROM-" + item.omna_product_id,
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


    def unlink_products(self):
        try:
            result_list = self.env['product.template'].search([('id', 'in', self._context.get('active_ids'))])
            parameters = {
                "data": {
                    "product_ids": result_list.mapped('omna_product_id'),
                    "integration_ids": [self.integration_id.integration_id],
                    "delete_from_integration": False
                }
            }

            temp_result = self.delete('products/link', parameters)

            for item in result_list:
                item.with_context(synchronizing=True).write({'integration_linked_ids': [(3, self.integration_id.id)], 'active_on_sale': False})

            self.env.cr.commit()
            self.env.user.notify_channel('info',
                                         'Por favor revise el resultado de la tarea en Ebanux u Odoo.',
                                         u"Información", True)

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
        pass


    def publish_products(self):
        try:
            result_list = self.env['product.template'].search([('id', 'in', self._context.get('active_ids'))])
            parameters = {
                "data": [{
                    "product_id": item.omna_product_id,
                    "properties": [
                        {
                            "id": "active",
                            "value": True
                        },
                        {
                            "id": "visibility",
                            "value": "both"
                        },
                        {
                            "id": "available_for_order",
                            "value": True
                        }
                    ]
                } for item in result_list]
            }

            temp_result = self.post('integrations/%s/products' % (self.integration_id.integration_id,), parameters)

            for item in result_list:
                item.integration_ids.write({'active_on_sale': False})

            self.env.cr.commit()
            self.env.user.notify_channel('info',
                                         'Por favor revise el resultado de la tarea en Ebanux u Odoo.',
                                         u"Información", True)

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
        pass


    def update_products(self):
        try:
            result_list = self.env['product.template'].search([('id', 'in', self._context.get('active_ids'))])
            query1 = []
            for item in result_list:
                new_price = 0

                if item.taxes_id.price_include:
                    aux_price = item.omna_tax_id.amount + 100
                    to_round = item.list_price / (aux_price / 100)
                    formatted_string = str(truncate(to_round, 6))
                    new_price = round(to_round, 5) if int(formatted_string[-1]) <= 5 else round(to_round, 6)
                if not item.taxes_id.price_include:
                    new_price = item.list_price

                data = {
                    "product_id": item.omna_product_id,
                    'name': item.name,
                    'description': item.description,
                    'price': new_price,
                    'package': {'weight': item.peso,
                                'height': item.alto,
                                'length': item.longitud,
                                'width': item.ancho,
                                'content': "No definido",
                                'overwrite': item.overwrite}
                }

                query1.append(data)

            response = self.put('products', {'data': query1})

            parameters = {
                "data": [{
                    "product_id": item.omna_product_id,
                    "properties": [
                        # {
                        #     "id": "category_id",
                        #     "value": item.category_ids[0].omna_category_id
                        # },
                        # {
                        #     "id": "other_categories",
                        #     "value": [X.omna_category_id for X in item.category_ids]
                        # },
                        {
                            "id": "brand_id",
                            # "value": self.product_template_id.brand_ids.omna_brand_id
                            "value": item.product_brand_id.omna_brand_id
                        },
                        {
                            "id": "reference",
                            "value": item.default_code
                        },
                        {
                            "id": "description_short",
                            "value": item.description_sale
                        },
                        {
                            "id": "id_tax_rules_group",
                            "value": int(item.omna_tax_id.omna_tax_rule_id)
                        }
                    ]
                } for item in result_list]
            }

            temp_result = self.post('integrations/%s/products' % (self.integration_id.integration_id,), parameters)

            query_list = temp_result.get('data')
            stock_list = []
            stock_location_id = self.env['stock.location'].search([('integration_id', '=', self.integration_id.id)])
            for query_item in query_list:
                # https://cenit.io/app/ecapi-v1/products/{product_id}/stock/items
                stock_result = self.get('products/%s/stock/items' % (query_item.get('id'), ))
                stock_result = stock_result.get('data')[0]
                stock_data = {
                    'omna_id': stock_result.get('id', False),
                    'integration_id': self.integration_id.id,
                    'stock_location_id': stock_location_id.id,
                    'product_product_name': "[%s]" % query_item.get('name'),
                    'product_template_name': query_item.get('name'),
                    'product_product_omna_id': stock_result.get('variant').get('id'),
                    'product_template_omna_id': query_item.get('id'),
                    'count_on_hand': stock_result.get('count_on_hand', 0),
                }
                stock_list.append(stock_data)


            self.env['omna.stock.items'].create(stock_list)
            self.env.cr.commit()

            self.env.user.notify_channel('info',
                                         'Por favor revise el resultado de la tarea en Ebanux u Odoo.',
                                         u"Información", True)
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
        pass

