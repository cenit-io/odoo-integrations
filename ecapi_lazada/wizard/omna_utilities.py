# -*- coding: utf-8 -*-

import requests
import base64
import json
import logging
import xmltodict
from datetime import datetime, timezone, time, timedelta
from odoo.exceptions import ValidationError
from odoo import models, api, exceptions, fields
# from odoo.addons.ecapi_lazada.library import prestashop_api


_logger = logging.getLogger(__name__)


class OmnaUtilities(models.TransientModel):
    _name = 'omna.utilities'
    _inherit = 'omna.api'


    omna_id = fields.Char('Omna Product ID')
    omna_ids = fields.Text('Omna Product IDs')
    integration_id = fields.Many2one('omna.integration', 'Integration')
    function_selection = fields.Selection([('unlink_one_product', 'Unlink One Product'), ('unlink_multi_products', 'Unlink Multi Products'), ('delete_unlinked_products', 'Delete Unlinked Products'),
                                           ('delete_one_product', 'Delete One Product'), ('delete_multi_products', 'Delete Multi Products'), ('get_one_product', 'Get One Product'),
                                           ('test_cron_api', 'Test Cron Api'), ('native_prestashop_api', 'Native Prestashop Api')], string='Operation')



    def execute_action(self):
        if self.function_selection == "unlink_one_product":
            self.unlink_one_product()
        if self.function_selection == "unlink_multi_products":
            self.unlink_multi_products()
        if self.function_selection == "delete_unlinked_products":
            self.delete_unlinked_products()
        if self.function_selection == "delete_one_product":
            self.delete_one_product()
        if self.function_selection == "delete_multi_products":
            self.delete_multi_products()
        if self.function_selection == "test_cron_api":
            self.test_cron_api()
        if self.function_selection == "get_one_product":
            self.get_one_product()
        if self.function_selection == "native_prestashop_api":
            self.native_prestashop_api()

        form_view_id = self.env.ref('ecapi_lazada.view_omna_utilities_wizard').id

        return {'type': 'ir.actions.act_window_close'}

        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Omna Utilities',
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'omna.utilities',
        #     'views': [[form_view_id, "form"]],
        #     'res_id': self.id,
        #     'context': self.env.context,
        #     'target': 'new',
        # }


    def unlink_one_product(self):
        try:

            temp_result = self.delete('products/%s/link' % (self.omna_id,), {"data": {"integration_ids": ["prestasho_col3"],"delete_from_integration": False}})
            self.env.user.notify_channel('info',
                                         'Por favor revise el resultado de la tarea en Ebanux u Odoo.',
                                         u"Información", True)

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
        pass


    def unlink_multi_products(self):
        try:
            parameters = {
                "data": {
                    "product_ids": self.omna_ids.split(';'),
                    "integration_ids": ["prestasho_col3"],
                    "delete_from_integration": False
                }
            }


            temp_result = self.delete('products/link', parameters)
            self.env.user.notify_channel('info',
                                         'Por favor revise el resultado de la tarea en Ebanux u Odoo.',
                                         u"Información", True)

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
        pass


    def delete_unlinked_products(self):
        try:
            # https://cenit.io/app/ecapi-v1/products/all
            temp_result = self.delete('products/all')
            self.env.user.notify_channel('info',
                                         'Por favor revise el resultado de la tarea en Ebanux u Odoo.',
                                         u"Información", True)

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
        pass


    def delete_one_product(self):
        try:
            # https://cenit.io/app/ecapi-v1/products/{product_id}
            temp_result = self.delete('products/%s' % (self.omna_id,))
            self.env.user.notify_channel('info',
                                         'Por favor revise el resultado de la tarea en Ebanux u Odoo.',
                                         u"Información", True)

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
        pass


    def delete_multi_products(self):
        try:
            parameters = {
                "data": {
                    "product_ids": self.omna_ids.split(';'),
                }
            }
            # https://cenit.io/app/ecapi-v1/products
            temp_result = self.delete('products', parameters)
            self.env.user.notify_channel('info',
                                         'Por favor revise el resultado de la tarea en Ebanux u Odoo.',
                                         u"Información", True)

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
        pass


    def test_cron_api(self):
        record_id = self.env.ref('ecapi_lazada.test_omna_delayed_cron').id
        data = {'active': True, 'nextcall': (datetime.now() + timedelta(minutes=3)).strftime('%Y-%m-%d %H:%M:%S'), 'user_id': self.env.uid}
        self.env['ir.cron'].browse(record_id).write(data)
        return True


    def test_delayed_function(self):
        self.env.user.notify_channel('info',
                                     'Ejemplo de función ejecutada en background.',
                                     u"Información", True)
        return True


    def get_one_product(self):
        try:
            # GET https://cenit.io/app/ecapi-v1/products/{product_id}
            # GET https://cenit.io/app/ecapi-v1/integrations/{integration_id}/products/{product_id}
            if self.integration_id:
                temp_result = self.get('integrations/%s/products/%s' % (self.integration_id.integration_id, self.omna_id,))

            if not self.integration_id:
                temp_result = self.get('products/%s' % (self.omna_id,))

            self.env.user.notify_channel('info',
                                         'Por favor revise el resultado de la tarea en Ebanux u Odoo.',
                                         u"Información", True)

        except Exception as e:
            _logger.error(e)
            raise exceptions.ValidationError(e)
        pass


    def native_prestashop_api(self):
        pass
        # prestashop_base_url = self.env['ir.config_parameter'].sudo().get_param("ecapi_lazada.prestashop_base_url", default='https://qa.futurevisions.com.pe')
        # prestashop_ws_key = self.env['ir.config_parameter'].sudo().get_param("ecapi_lazada.prestashop_ws_key")
        # api = prestashop_api.PrestashopApi(prestashop_base_url + '/api', prestashop_ws_key)
        #
        # print('Edit')
        # data = {'stock_availables': {
        #     "id": 27300,
        #     "id_product": 2727,
        #     "id_product_attribute": 12853,
        #     "quantity": 250,
        #     "depends_on_stock": 0,
        #     "out_of_stock": 2,
        #     "id_shop": 0,
        #     "id_shop_group": 1
        # }}
        # res = api.edit('stock_availables', data)['stock_available']
        # print(res)
        # return True
