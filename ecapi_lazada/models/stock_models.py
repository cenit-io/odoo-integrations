# -*- coding: utf-8 -*-

import odoo
from datetime import *
from odoo import models, fields, api, exceptions, tools, _
from odoo.exceptions import UserError
from odoo.tools.image import image_data_uri
from odoo.tools import float_compare, pycompat
from odoo.tools import ImageProcess
# from odoo.addons.ecapi_lazada.library import prestashop_api
import dateutil.parser
import werkzeug
import pytz
import json
import os
import base64
import logging
import time
import threading
import string
import random


_logger = logging.getLogger(__name__)


class OmnaStockItems(models.Model):
    _name = 'omna.stock.items'
    _inherit = 'omna.api'


    omna_id = fields.Char("Stock Item ID", index=True)
    integration_id = fields.Many2one('omna.integration', 'OMNA Integration', required=True, ondelete='cascade', index=True)
    stock_location_id = fields.Many2one('stock.location', string='Stock Location', required=True, ondelete='cascade', index=True)
    product_product_name = fields.Char(string='Variant name')
    product_template_name = fields.Char(string='Product name')
    product_product_sku = fields.Char(string="Variant sku")
    product_template_sku = fields.Char(string="Product sku")
    product_product_omna_id = fields.Char(string="Variant OMNA ID")
    product_template_omna_id = fields.Char(string="Product OMNA ID")
    count_on_hand = fields.Integer(string="Count on hand")

    def update_omna_stock(self, stock_move_line_list):
        pass
        # stock_move_line_result = self.env["stock.move.line"].search([('id', 'in', stock_move_line_list)])
        # # stock_move_line_result = stock_move_line_list
        # for res in stock_move_line_result:
        #     if res.product_id.product_tmpl_id.integration_ids and res.product_id.product_tmpl_id.integration_linked_ids and res.product_id.product_tmpl_id.omna_product_id:
        #         data = {"data": {"quantity": int(res.qty_done)}}
        #         # integration_id = res.location_dest_id.integration_id.integration_id if res.location_dest_id.omna_id else res.location_id.integration_id.integration_id
        #         integration_id = res.product_id.product_tmpl_id.integration_linked_ids.integration_id
        #         omna_product_id = res.product_id.omna_product_id
        #         omna_variant_id = res.product_id.omna_variant_id
        #
        #         query_param = {'integration_id': integration_id}
        #         if omna_product_id:
        #             query_param.update({'product_id': omna_product_id})
        #         if omna_variant_id:
        #             query_param.update({'variant_id': omna_variant_id})
        #         query_result = self.get('stock/items', query_param)
        #         # qty = response.get('data')[0].get('count_on_hand')
        #         omna_stock_item_id = query_result.get('data')[0].get('id')
        #         # omna_stock_item_result = self.search([('omna_id', '=', omna_stock_item_id), ('integration_id.integration_id', '=', integration_id)])
        #         omna_stock_item_result = self.search([('omna_id', '=', omna_stock_item_id)])
        #
        #         if (res.picking_id.picking_type_id.code == 'incoming'):
        #             data['data']['quantity'] = int(1 * res.qty_done)
        #             response1 = self.post('stock/items/%s' % (omna_stock_item_id,), data)
        #             omna_stock_item_result.write({'count_on_hand': data['data']['quantity']})
        #         if (res.picking_id.picking_type_id.code == 'outgoing'):
        #             data['data']['quantity'] = int(-1 * res.qty_done)
        #             response2 = self.post('stock/items/%s' % (omna_stock_item_id,), data)
        #             omna_stock_item_result.write({'count_on_hand': data['data']['quantity']})
        #             # https://cenit.io/app/ecapi-v1/integrations/{integration_id}/products/{product_id}/variants/{variant_id}
        #             variant_remote = self.get('integrations/%s/products/%s/variants/%s' % (integration_id,
        #                                                                                    omna_stock_item_result.product_template_omna_id,
        #                                                                                    omna_stock_item_result.product_product_omna_id))
        #             variant_data = variant_remote.get('data').get('integration').get('variant')
        #
        #             # https://cenit.io/app/ecapi-v1/integrations/prestashop_col10/call/native/service
        #             data_aux = {"data": {"path": "/stock_availables",
        #                                  "method": "GET",
        #                                  "params": {"display": "full",
        #                                             "filter[id_product]": variant_data.get('remote_product_id'),
        #                                             "filter[id_product_attribute]": variant_data.get('remote_variant_id')}}}
        #             response3 = self.post('integrations/%s/call/native/service' % (integration_id,), data_aux)
        #             external_adjust = response3.get('data').get('stock_availables')[0]
        #
        #             lazada_base_url = self.env['ir.config_parameter'].sudo().get_param("ecapi_lazada.lazada_base_url", default='https://qa.futurevisions.com.pe')
        #             lazada_ws_key = self.env['ir.config_parameter'].sudo().get_param("ecapi_lazada.lazada_ws_key")
        #             api = lazada_api.PrestashopApi(lazada_base_url + '/api', lazada_ws_key)
        #
        #             print('Edit')
        #             to_update_data = {'stock_availables': external_adjust}
        #             to_update_data['stock_availables']['quantity'] = external_adjust['quantity'] + res.qty_done
        #             res = api.edit('stock_availables', to_update_data)['stock_available']
        #             print(res)
        #
        #         if not (res.picking_id.picking_type_id.code):
        #             omna_stock_item_result.reset_quantity(data)



    def reset_quantity(self, data):
        # https://cenit.io/app/ecapi-v1/stock/items
        query_param = {'integration_id': self.integration_id.integration_id}
        if self.product_template_omna_id:
            query_param.update({'product_id': self.product_template_omna_id})
        if self.product_product_omna_id:
            query_param.update({'variant_id': self.product_product_omna_id})
        response = self.get('stock/items', query_param)
        qty = response.get('data')[0].get('count_on_hand')
        omna_stock_item_id = response.get('data')[0].get('id')

        # https://cenit.io/app/ecapi-v1/stock/items/{stock_item_id}
        to_reset = {"data": {"quantity": -1 * qty}}
        response = self.post('stock/items/%s' % (omna_stock_item_id,), to_reset)
        response = self.post('stock/items/%s' % (omna_stock_item_id,), data)
        aux = self.count_on_hand
        self.write({'count_on_hand': -1 * aux})
        self.write({'count_on_hand': data['data']['quantity']})

    
    def write(self, values):
        # for item in self:
        if values.get('count_on_hand'):
            values['count_on_hand'] = self.count_on_hand + values.get('count_on_hand')
        return super(OmnaStockItems, self).write(values)




class StockMoveLine(models.Model):
    _name = "stock.move.line"
    _inherit = ['stock.move.line', 'omna.api']


    def write(self, vals):
        result = super(StockMoveLine, self).write(vals)
        # Agregar validacion o filtro para solo aplicar esta funcionalidad a los productos que se encuentran en Cenit y Prestashop respectivamente.
        stock_move_line_list = [X.id for X in self]
        record_id = self.env.ref('ecapi_lazada.ecapi_lazada_inventory_cron').id
        data = {'active': True,
                'nextcall': (datetime.now() + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S'),
                'user_id': self.env.uid,
                'code': "model.update_omna_stock(%s)" % (str(stock_move_line_list))}
        self.env['ir.cron'].browse(record_id).write(data)

        # start_time = threading.Timer(15, self.env['omna.stock.items'].update_omna_stock, args=(self,))
        # start_time.start()

        # self.env['omna.stock.items'].update_omna_stock(stock_move_line_list)
        return result



class Picking(models.Model):
    _name = "stock.picking"
    _inherit = 'stock.picking'


    show_warning_wh = fields.Boolean(compute='_show_warning_wh')
    show_warning_op = fields.Selection([('orig', 'Orig'), ('dest', 'Dest')], compute='_show_warning_wh')



    # @api.depends('picking_id.picking_type_id', 'product_id.tracking')
    def _show_warning_wh(self):
        for item in self:
            sale = item.sale_id
            if item.location_id:
                item.show_warning_op = 'orig'
            if item.location_dest_id:
                item.show_warning_op = 'dest'
            if sale.omna_order_reference and sale.integration_name:
                item.show_warning_wh = True
            else:
                item.show_warning_wh = False



# class StockItemLog(models.Model):
#     _name = 'stock.item.log'
#
#
#
#     integration_id = fields.Many2one('omna.integration', 'OMNA Integration', required=True, ondelete='cascade', index=True)
#     stock_location_id = fields.Many2one('stock.location', string='Stock Location', required=True, ondelete='cascade', index=True)
#     variant_name = fields.Char(string='Variant name')
#     product_name = fields.Char(string='Product name')
#     variant_sku = fields.Char(string="Variant sku")
#     product_sku = fields.Char(string="Product sku")
#     omna_variant_id = fields.Char(string="Variant OMNA ID")
#     omna_product_id = fields.Char(string="Product OMNA ID")
#     count_moved = fields.Integer(string="Count moved")
#     moved_description = fields.Text(string="Description")




