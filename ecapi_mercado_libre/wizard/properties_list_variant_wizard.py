# -*- coding: utf-8 -*-

import logging, odoo
from datetime import datetime, timezone
import dateutil.parser
from odoo import models, api, exceptions, fields, _
import pytz

_logger = logging.getLogger(__name__)


class PropertiesListVariantWizard(models.TransientModel):
    _name = 'properties.list.variant.wizard'
    _inherit = 'omna.api'



    def _get_category_id(self):
        product_template_obj = self.env['product.template']
        product = product_template_obj.search([('id', '=', self.env.context.get('default_product_template_id', False))])
        aux = list(filter(lambda lolo: lolo.integration_id.id == self.env.context.get('integration_id', False), product.category_ids))
        if aux:
            return aux[0]
        else:
            return False



    def _get_category_domain(self):
        product_category_obj = self.env['product.category']
        result = product_category_obj.search([('integration_id', '=', self.env.context.get('integration_id', False))]).ids
        if result:
            return [('id', 'in', result)]
        else:
            return [('id', '=', -1)]



    # def _get_property_primary_domain(self):
    #     integration_properties_obj = self.env['integration.properties']
    #     result = integration_properties_obj.search([('integration_id', '=', self.env.context.get('integration_id', False))]).ids
    #     if result:
    #         return [('id', 'in', result)]
    #     else:
    #         return [('id', '=', -1)]


    def _get_property_value_ids(self):
        integration_properties_obj = self.env['integration.properties']
        product_template_obj = self.env['product.template']
        properties_values_obj = self.env['properties.values.variant']
        omna_integration_obj = self.env['omna.integration']
        result = properties_values_obj.search(
            ['&', '|', ('product_product_id', '=', self.env.context.get('default_product_product_id', False)),
             ('integration_id', '=', self.env.context.get('integration_id', False)),
             ('property_name', '!=', 'category_id')]).ids
        if result:
            return result
        else:
            return []


    def _get_omna_integration_id(self):
        omna_integration_obj = self.env['omna.integration']
        result = omna_integration_obj.search([('id', '=', self.env.context.get('integration_id', False))]).ids
        if result:
            return result[0]
        else:
            return False



    # property_value_ids = fields.Many2many('properties.values', string='Property List')
    # property_value_primary_ids = fields.Many2many('properties.values', default=_get_property_value_primary_ids, string='Property Primary List')
    # omna_integration_id = fields.Many2one('omna.integration', 'Integration', required=True, default=_get_omna_integration_id)
    omna_integration_id = fields.Many2one('omna.integration', 'Integration', required=True, domain=lambda self:[('company_id', '=', self.env.company.id)])
    # category_id = fields.Many2one('product.category', 'Category', required=True, default=_get_category_id, domain=_get_category_domain)
    category_id = fields.Many2one('product.category', 'Category', required=True, domain=_get_category_domain)
    # property_value_ids = fields.Many2many('properties.values.variant', default=_get_property_value_ids, string='Property List')
    property_value_ids = fields.Many2many('properties.values.variant', string='Property List')

    @api.onchange('omna_integration_id')
    def _onchange_omna_integration_id(self):
        # integration_properties_obj = self.env['integration.properties']
        # product_template_obj = self.env['product.template']
        product_category_obj = self.env['product.category']
        # omna_integration_obj = self.env['omna.integration']

        result = product_category_obj.search([('integration_id', '=', self.omna_integration_id.id)]).ids
        if result:
            return {'domain': {'category_id': [('id', 'in', result), ('omna_category_id', '!=', False)] } }
        else:
            return {'domain': {'category_id': [('id', '=', -1)] } }



    def get_properties_variant(self):
        integration_properties_obj = self.env['integration.properties']
        product_template_obj = self.env['product.template']
        product_product_obj = self.env['product.product']
        properties_values_variant_obj = self.env['properties.values.variant']
        omna_integration_obj = self.env['omna.integration']


        integration = omna_integration_obj.search([('id', '=', self.omna_integration_id.id)])
        product = product_template_obj.search([('id', '=', self.env.context.get('default_product_template_id'))])
        variant = product_product_obj.search([('id', '=', self.env.context.get('default_product_product_id', False))])
        # https://cenit.io/app/ecapi-v1/products/{product_id}/variants/{variant_id}
        remote_variant = product_product_obj.get('products/%s/variants/%s' % (product.omna_product_id, variant.omna_variant_id))
        # aux2 = list(filter(lambda lolo: lolo.integration_id.id == integration.id, variant.category_ids))
        aux2 = next((i for i in variant.category_ids if i.integration_id.id == integration.id), False)
        if not aux2:
            variant.with_context(synchronizing=True).write({'category_ids': [(4, self.category_id.id)]})
            self.env.cr.commit()

        temp = {
            "data": {
                "properties": [
                    {
                        "id": "category_id",
                        "value": self.category_id.omna_category_id
                    }
                ]
            }
        }
        # https: // cenit.io / app / ecapi - v1 / integrations / {integration_id} / products / {remote_product_id} / variants / {remote_variant_id}
        try:
            response = product_product_obj.post('integrations/%s/products/%s/variants/%s' % (integration.integration_id, "PENDING-PUBLISH-FROM-" + product.omna_product_id, "PENDING-PUBLISH-FROM-" + variant.omna_variant_id),temp)
        except Exception as error:
            pass
            # message = "Not found product with remote_product_id '%s'" % ("PENDING-PUBLISH-FROM-" + product.omna_product_id)
            # if error.name.find(message) != -1:
            #     response = product_product_obj.post('integrations/%s/products/%s/variants/%s' % (integration.integration_id, product.omna_product_id, variant.omna_variant_id),temp)
            # _logger.error(error)


        response = product_product_obj.get('integrations/%s/products/%s/variants/%s' % (integration.integration_id, "PENDING-PUBLISH-FROM-" + product.omna_product_id, "PENDING-PUBLISH-FROM-" + variant.omna_variant_id))
        # response = product_product_obj.get('integrations/%s/products/%s/variants/%s' % (integration.integration_id, product.omna_product_id, variant.omna_variant_id))
        # response = product_product_obj.get('integrations/lazada_odoo_test_co_sg/products/1622435953/variants/7636497121')
        remote_result = response.get('data').get('integration').get('variant').get('properties')
        data_result = response.get('data')
        lolo = [x.get('id') for x in remote_result if x.get('id') != 'category_id']

        # result = properties_values_variant_obj.search(['&', '&', ('product_product_id', '=', variant.id), ('integration_id', '=', integration.id), ('property_name', 'in', lolo)]).ids
        result = properties_values_variant_obj.search([('product_product_id', '=', variant.id), ('integration_id', '=', integration.id)]).ids
        if result:
            self.property_value_ids = result
        else:
            integration_ids = integration_properties_obj.search_read([('integration_id', '=', integration.id)], ['property_name'])
            values_list = []

            if not integration_ids:
                if remote_result:
                    for item in remote_result:
                        values_list.append({
                            'property_name': item.get('id'),
                            'property_type': item.get('input_type'),
                            'integration_id': integration.id,
                            'property_category': 'integration_property',
                            'property_label': item.get('label'),
                            'property_required': item.get('required'),
                            'property_readonly': item.get('read_only'),
                            'property_options': str(item.get('options')),
                            'property_options_service_path': item.get('options_service_path'),
                            'value_option_ids': [(0, 0, {'option_value': res}) for res in item.get('options')] if item.get('input_type') in ['single_select', 'multi_select', 'enum_input', 'multi_enum_input'] else []
                        })

                    integration_properties_obj.create(values_list)
                    self.env.cr.commit()

            values_list.clear()
            if integration_ids:
                items_difference = set([x.get('id') for x in remote_result]).difference(set([z.get('property_name') for z in integration_ids]))
                list_aux = list(filter(lambda d: d.get('id') in items_difference, remote_result))
                for item in list_aux:
                    values_list.append({
                        'property_name': item.get('id'),
                        'property_type': item.get('input_type'),
                        'integration_id': integration.id,
                        'property_category': 'integration_property',
                        'property_label': item.get('label'),
                        'property_required': item.get('required'),
                        'property_readonly': item.get('read_only'),
                        'property_options': str(item.get('options')),
                        'property_options_service_path': item.get('options_service_path'),
                        'value_option_ids': [(0, 0, {'option_value': res}) for res in item.get('options')] if item.get('input_type') in ['single_select', 'multi_select', 'enum_input', 'multi_enum_input'] else []
                    })
                integration_properties_obj.create(values_list)
                self.env.cr.commit()

            lolo.append('category_id')
            integration_ids = integration_properties_obj.search([('integration_id', '=', integration.id), ('property_name', 'in', lolo)])
            values_list.clear()
            if integration_ids:
                for item in integration_ids:
                    values_list.append({
                        'property_id': item.id,
                        'product_product_id': variant.id,
                        'property_value': 'default_value',
                        # 'integration_id': item.integration_id.id,
                        # 'property_name': item.property_name,
                        # 'property_label': item.property_label,
                        # 'property_category': item.property_category,
                        # 'property_options': "Posibles valores a asignar: " + item.property_options,
                        # 'property_options_service_path': "Valores a asignar relacionados en: " + item.property_options_service_path if item.property_options_service_path else ""
                    })

                properties_values_variant_obj.create(values_list)
                self.env.cr.commit()

                lolo.remove('category_id')
                self.property_value_ids = properties_values_variant_obj.search(['&', '&', ('product_product_id', '=', variant.id), ('integration_id', '=', integration.id), ('property_name', 'in', lolo)]).ids


        form_view_id = self.env.ref('ecapi_mercado_libre.view_properties_list_variant_wizard').id
        # your logics
        return {
            'type': 'ir.actions.act_window',
            'name': 'Property List By Integrations',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'properties.list.variant.wizard',
            'views': [[form_view_id, "form"]],
            'res_id': self.id,
            'context': self.env.context,
            'target': 'new',
        }




    def save_all_values(self):
        return {'type': 'ir.actions.act_window_close'}



    def publish_product_variant(self):
        integration_properties_obj = self.env['integration.properties']
        product_template_obj = self.env['product.template']
        properties_values_obj = self.env['properties.values']
        omna_integration_obj = self.env['omna.integration']
        product = product_template_obj.search([('id', '=', self.env.context.get('default_product_template_id', False))])
        # product.write({'category_ids': [(4, self.category_id.id)]})
        # self.env.cr.commit()
        #
        # self._onchange_property_primary_id()
        # https: // cenit.io / app / ecapi - v1 / integrations / {integration_id} / products / {remote_product_id}
        # https: // cenit.io / app / ecapi - v1 / integrations / {integration_id} / products / {remote_product_id}
        # aux = omna_integration_obj.search([('id', '=', self.env.context.get('integration_id', False))])
        temp = {
            "data": {
                "properties": [
                    {
                        "id": "price",
                        "value": 3
                    }
                ]
            }
        }
        response = product_template_obj.post('integrations/%s/products/%s' % (self.omna_integration_id.integration_id, "PENDING-PUBLISH-FROM-"+product.omna_product_id), temp)
        # response = product_template_obj.get('integrations/%s/products/%s' % (aux.integration_id, "PENDING-PUBLISH-FROM-"+product.omna_product_id))
        # remote_result = response.get('data').get('integrations')[0].get('product').get('properties')
        return {'type': 'ir.actions.act_window_close'}
        # form_view_id = self.env.ref('omna.view_properties_values_wizard').id
        # # your logics
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Property List By Integrations',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'properties.values.wizard',
        #     'views': [[form_view_id, "form"]],
        #     'res_id': self.id,
        #     'context': self.env.context,
        #     'target': 'new',
        # }
