# -*- coding: utf-8 -*-

import logging, odoo
from datetime import datetime, timezone
import dateutil.parser
from odoo import models, api, exceptions, fields, _
import pytz
from odoo import tools

_logger = logging.getLogger(__name__)

# Todo lo que se implementó en base a la categoría, deberá modificarse y reajustarse a la relación con marca de producto
# Tener presente las funciones de valores por default, domains, on_changes y otras
# El campo de omna_integration_id no será editable, ya que el wizard se muestra de forma contextual a una integración específica

class PropertiesValuesWizard(models.TransientModel):
    _name = 'properties.values.wizard'
    _inherit = 'omna.api'



    def _get_property_value_ids(self):
        # integration_properties_obj = self.env['integration.properties']
        product_template_obj = self.env['product.template']
        properties_values_obj = self.env['properties.values.product']
        # omna_integration_obj = self.env['omna.integration']
        result = properties_values_obj.search(['&','&',('product_template_id', '=', self.env.context.get('default_product_template_id', False)),
                                                       ('integration_id', '=', self.env.context.get('integration_id', False)),
                                               ('property_name', '!=', 'category_id')]).ids
        if result:
            return result
        else:
            return []


    def _get_omna_integration_id(self):
        omna_integration_obj = self.env['omna.integration']
        return omna_integration_obj.search([('id', '=', self.env.context.get('integration_id', False))]).id
        # result = omna_integration_obj.search([('id', '=', self.env.context.get('integration_id', False))]).ids
        # if result:
        #     return result[0]
        # else:
        #     return False



    omna_integration_id = fields.Many2one('omna.integration', 'Integration to Link', required=True, default=_get_omna_integration_id, domain=lambda self:[('company_id', '=', self.env.company.id)])
    property_value_ids = fields.Many2many('properties.values.product', default=_get_property_value_ids, string='Property List')




    def get_properties_product(self):
        pass
        # integration_properties_obj = self.env['integration.properties']
        # product_template_obj = self.env['product.template']
        # properties_values_obj = self.env['properties.values']
        # omna_integration_obj = self.env['omna.integration']
        # integration = omna_integration_obj.search([('id', '=', self.env.context.get('integration_id', False))])
        # product = product_template_obj.search([('id', '=', self.env.context.get('default_product_template_id', False))])
        # product.write({'brand_ids': self.brand_id.id})
        # self.env.cr.commit()
        #
        # temp = {
        #     "data": {
        #         "properties": [
        #             {
        #                 "id": "category_id",
        #                 "value": product.categ_id.omna_category_id
        #             },
        #             {
        #                 "id": "brand_id",
        #                 "value": product.brand_ids.omna_brand_id
        #             }
        #         ]
        #     }
        # }
        #
        # # response1 = product_template_obj.post('integrations/%s/products/%s' % (integration.integration_id, product.omna_product_id), temp)
        #
        # response = product_template_obj.get('integrations/%s/products/%s' % (integration.integration_id, product.omna_product_id), {'with_details': True})
        #
        #
        # result = properties_values_obj.search(['&','&',('product_template_id', '=', product.id), ('integration_id', '=', integration.id), ('property_name', '!=', 'category_id')]).ids
        # if result:
        #     self.property_value_ids = result
        # else:
        #     remote_result = response.get('data').get('integration').get('product').get('properties')
        #     data_result = response.get('data')
        #     # lolo = [x.get('id') for x in remote_result]
        #     properties_filter = [x.get('id') for x in remote_result if x.get('id') not in ['active', 'category_id', 'brand_id']]
        #     exist_properties = integration_properties_obj.search_read([('integration_id', '=', integration.id)], ['property_name'])
        #
        #     values_list = []
        #     aux_list = []
        #
        #     if not exist_properties:
        #         if remote_result:
        #             for item in remote_result:
        #                 value_collection = []
        #                 values_list.append({
        #                     'property_name': item.get('id'),
        #                     'property_type': item.get('input_type'),
        #                     'integration_id': integration.id,
        #                     'property_category': 'integration_property',
        #                     'property_label': item.get('label'),
        #                     'property_required': item.get('required'),
        #                     'property_readonly': item.get('read_only'),
        #                     'property_options': str(item.get('options')),
        #                     'property_options_service_path': item.get('options_service_path'),
        #                     'value_option_ids': [(0, 0, {'option_value': res.get('value', -1) or -1, 'option_label': res.get('label', "-") or "-"}) for res in item.get('options')] if item.get('input_type') in ['single_select', 'multi_select', 'enum_input', 'multi_enum_input'] else []
        #                 })
        #
        #                 # res_list = [i for n, i in enumerate(test_list) if i not in test_list[n + 1:]]
        #                 # res_list = {frozenset(item.items()) : item for item in test_list}.values()
        #
        #                 if item.get('input_type') == "single_select_with_remote_options":
        #                     # lolo.extend([{'omna_attribute_value_id': res.get('id'),
        #                     #                                    'name': res.get('name')} for res in
        #                     #                            item.get('options')])
        #                     lolo = {frozenset(X.items()) : X for X in [{'omna_attribute_value_id': res.get('id'),
        #                                                        'name': res.get('name')} for res in
        #                                                item.get('options')]}.values()
        #                     a = [(0, 0, Y) for Y in lolo]
        #                     value_collection.extend(a)
        #                 if (item.get('input_type') == "single_select") and (item.get('label') != 'Color') :
        #                     # lolo.extend([{'omna_attribute_value_id': res.get('value', -1) or -1,
        #                     #                                    'name': res.get('label', "-") or "-"} for res in
        #                     #                            item.get('options')])
        #                     lolo = {frozenset(X.items()): X for X in [{'omna_attribute_value_id': res.get('value', -1) or -1,
        #                                                        'name': res.get('label', "-") or "-"} for res in
        #                                                item.get('options')]}.values()
        #                     b = [(0, 0, Y) for Y in lolo]
        #                     value_collection.extend(b)
        #                 if item.get('input_type') not in ["single_select", "single_select_with_remote_options"]:
        #                     # lolo.extend([{'omna_attribute_value_id': item.get('id'),
        #                     #                                    'name': item.get('label')}])
        #                     lolo = {frozenset(X.items()): X for X in
        #                                  [{'omna_attribute_value_id': item.get('id'),
        #                                    'name': item.get('label')}]}.values()
        #                     c = [(0, 0, Y) for Y in lolo]
        #                     value_collection.extend(c)
        #
        #                 aux_list.append({'name': item.get('label'),
        #                                  'omna_attribute_id': item.get('id'),
        #                                  'value_ids': value_collection})
        #                 # aux_list.append({'name': item.get('label'),
        #                 #                  'omna_attribute_id': item.get('id'),
        #                 #                  'value_ids': [(0, 0, {'omna_attribute_value_id': res.get('value', -1) or -1,
        #                 #                                        'name': res.get('label', "-") or "-"}) for res in
        #                 #                                item.get('options')]})
        #
        #             self.env['product.attribute'].create(aux_list)
        #             integration_properties_obj.create(values_list)
        #             self.env.cr.commit()
        #
        #     values_list.clear()
        #     aux_list.clear()
        #     if exist_properties:
        #         items_difference = set([x.get('id') for x in remote_result]).difference(set([z.get('property_name') for z in exist_properties]))
        #         list_aux = list(filter(lambda d: d.get('id') in items_difference, remote_result))
        #         for item in list_aux:
        #             values_list.append({
        #                 'property_name': item.get('id'),
        #                 'property_type': item.get('input_type'),
        #                 'integration_id': integration.id,
        #                 'property_category': 'integration_property',
        #                 'property_label': item.get('label'),
        #                 'property_required': item.get('required'),
        #                 'property_readonly': item.get('read_only'),
        #                 'property_options': str(item.get('options')),
        #                 'property_options_service_path': item.get('options_service_path'),
        #                 'value_option_ids': [(0, 0, {'option_value': res.get('value', -1), 'option_label': res.get('label', "-")}) for res in item.get('options')] if item.get('input_type') in ['single_select', 'multi_select', 'enum_input', 'multi_enum_input'] else []
        #             })
        #
        #             aux_list.append({'name': item.get('label'),
        #                              'omna_attribute_value_id': item.get('id')})
        #         self.env['product.attribute'].create(aux_list)
        #         integration_properties_obj.create(values_list)
        #         self.env.cr.commit()
        #
        #
        #     integration_ids = integration_properties_obj.search([('integration_id', '=', integration.id), ('property_name', 'in', properties_filter)])
        #     values_list.clear()
        #
        #     if integration_ids:
        #         for item in integration_ids:
        #             values_list.append({
        #                 'property_id': item.id,
        #                 'product_template_id': product.id,
        #                 'property_value': 'default_value'
        #             })
        #
        #         properties_values_obj.create(values_list)
        #         self.env.cr.commit()
        #         self.property_value_ids = properties_values_obj.search(['&', '&', ('product_template_id', '=', product.id), ('integration_id', '=', integration.id), ('property_name', '!=', 'category_id')]).ids
        #
        #
        # form_view_id = self.env.ref('ecapi_mercado_libre.view_properties_values_wizard').id
        # # your logics
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Property List By Integrations',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'properties.values.wizard',
        #     'views': [[form_view_id, "form"]],
        #     # 'domain': [('property_name','!=','category_id')],
        #     'res_id': self.id,
        #     'context': self.env.context,
        #     'target': 'new',
        # }


    def save_all_values(self):
        pass
        # # integration_properties_obj = self.env['integration.properties']
        # product_template_obj = self.env['product.template']
        # # product_product_obj = self.env['product.product']
        # properties_values_obj = self.env['properties.values.product']
        # # properties_values_variant_obj = self.env['properties.values.variant']
        # # omna_integration_product_obj = self.env['omna.integration_product']
        # product = product_template_obj.search([('id', '=', self.env.context.get('default_product_template_id', False))])
        # # product_variant = product_product_obj.search([('product_tmpl_id', '=', product.id)])
        # product_integration = omna_integration_product_obj.search([('product_template_id', '=', product.id), ('integration_ids', '=', self.omna_integration_id.id)])
        # product.write({'brand_ids': self.brand_id.id})
        # self.env.cr.commit()
        # # response_product = product_template_obj.get('integrations/%s/products/%s' % (integration.integration_id, "PENDING-PUBLISH-FROM-" + product.omna_product_id))
        # response_product = product_template_obj.get('integrations/%s/products/%s' % (product_integration.integration_ids.integration_id, product.omna_product_id), {'with_details': True})
        #
        # remote_result = response_product.get('data').get('integration').get('product').get('properties')
        #
        # temp_product = {"data": {"properties": []}}
        #
        # stored_values = properties_values_obj.search(
        #     [('integration_id', '=', product_integration.integration_ids.id), ('product_template_id', '=', product.id)])
        # for item in stored_values:
        #     if item.property_type == 'date':
        #         aux_date_value = datetime.strftime(item.property_date_value, '%Y-%m-%d')
        #         temp_product['data']['properties'].append({'id': item.property_name,
        #                                                    'value': aux_date_value})
        #     if item.property_type == 'boolean':
        #         temp_product['data']['properties'].append({'id': item.property_name,
        #                                                    'value': item.property_boolean_value})
        #     if item.property_type == 'numeric':
        #         temp_product['data']['properties'].append({'id': item.property_name,
        #                                                    'value': item.property_float_value})
        #     if item.property_type == 'text':
        #         temp_product['data']['properties'].append({'id': item.property_name,
        #                                                    'value': item.property_value})
        #     if item.property_type == 'rich_text':
        #         temp_product['data']['properties'].append({'id': item.property_name,
        #                                                    'value': item.property_rich_text_value})
        #     if item.property_type in ['single_select', 'enum_input']:
        #         temp_product['data']['properties'].append({'id': item.property_name,
        #                                                    'value': item.property_selection_value.option_value if item.property_selection_value.option_value != -1 else None})
        #     if item.property_type in ['multi_select', 'multi_enum_input']:
        #         temp_product['data']['properties'].append({'id': item.property_name,
        #                                                    'value': [x.option_value if x.option_value != -1 else None for x in
        #                                                              item.property_multi_selection_value]})
        #
        # temp_product['data']['properties'].append({'id': "category_id", 'value': product.categ_id.omna_category_id})
        # temp_product['data']['properties'].append({'id': "brand_id", 'value': product.brand_ids.omna_brand_id})
        # # product_integration.write({'active_on_sale': True})
        # # temp_product['data']['properties'].append({'id': 'active', 'value': True})
        # response2 = product_template_obj.post('integrations/%s/products/%s' % (product_integration.integration_ids.integration_id, product.omna_product_id), temp_product)
        #
        # self.env.user.notify_channel('info', _(
        #     'The task to update product properties on marketplace have been created, please go to "System\Tasks" to check out the task status.'),
        #                              _("Information"), True)
        #
        # return {'type': 'ir.actions.act_window_close'}



    def publish_product(self):
        pass
        # product_template_obj = self.env['product.template']
        # omna_integration_product_obj = self.env['omna.integration_product']
        # product = product_template_obj.search([('id', '=', self.env.context.get('default_product_template_id', False))])
        # product_integration = omna_integration_product_obj.search(
        #     [('product_template_id', '=', product.id), ('integration_ids', '=', self.omna_integration_id.id)])
        #
        # temp_product = {"data": {"properties": []}}
        #
        # product_integration.write({'active_on_sale': True})
        # temp_product['data']['properties'].append({'id': 'active', 'value': True})
        # # temp_product['data']['properties'].append({'id': 'sku', 'value': "EJEMPLO001"})
        # response = product_template_obj.post('integrations/%s/products/%s' % (
        # product_integration.integration_ids.integration_id, product.omna_product_id), temp_product)
        #
        # self.env.user.notify_channel('info', _(
        #     'The task to publish product on marketplace have been created, please go to "System\Tasks" to check out the task status.'),
        #                              _("Information"), True)
        #
        # return {'type': 'ir.actions.act_window_close'}



    def unpublish_product(self):
        pass
        # product_template_obj = self.env['product.template']
        # omna_integration_product_obj = self.env['omna.integration_product']
        # product = product_template_obj.search([('id', '=', self.env.context.get('default_product_template_id', False))])
        # product_integration = omna_integration_product_obj.search([('product_template_id', '=', product.id), ('integration_ids', '=', self.omna_integration_id.id)])
        #
        # temp_product = {"data": {"properties": []}}
        #
        # product_integration.write({'active_on_sale': False})
        # temp_product['data']['properties'].append({'id': 'active', 'value': False})
        # response = product_template_obj.post('integrations/%s/products/%s' % (product_integration.integration_ids.integration_id, product.omna_product_id), temp_product)
        #
        # self.env.user.notify_channel('info', _(
        #     'The task to unpublish product on marketplace have been created, please go to "System\Tasks" to check out the task status.'),
        #                              _("Information"), True)
        #
        # return {'type': 'ir.actions.act_window_close'}


