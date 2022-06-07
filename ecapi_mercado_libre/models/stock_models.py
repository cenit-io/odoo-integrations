# -*- coding: utf-8 -*-

import odoo
from datetime import *
from odoo import models, fields, api, exceptions, tools, _
from odoo.exceptions import UserError
from odoo.tools.image import image_data_uri
from odoo.tools import float_compare, pycompat
from odoo.tools import ImageProcess
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
    integration_id = fields.Many2one('omna.integration', 'Integration', required=True, ondelete='cascade', index=True)
    stock_warehouse_id = fields.Many2one('stock.warehouse', string='Location', required=True, ondelete='cascade', index=True)
    product_product_name = fields.Char(string='Variant name')
    product_template_name = fields.Char(string='Product name')
    product_product_sku = fields.Char(string="SKU Variant")
    product_template_sku = fields.Char(string="Product sku")
    product_product_omna_id = fields.Char(string="Variant ECAPI ID")
    product_template_omna_id = fields.Char(string="Product ECAPI ID")
    count_on_hand = fields.Integer(string="Quantity")
    previous_quantity = fields.Integer(string='Previous Quantity')

    def update_omna_stock(self):
        self.write({'previous_quantity': self.count_on_hand})
        view_id = self.env.ref('ecapi_mercado_libre.wizard_stock_item_mov_view').id
        context = dict(
            self.env.context,
            integration_id=self.integration_id.integration_id,
            omna_product_id=self.product_template_omna_id,
            omna_variant_id=self.product_product_omna_id,
            omna_stock_item_id=self.omna_id,
            count_on_hand=self.count_on_hand,
        )
        return {
            'name': 'Actualizar Cantidad',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.stock.item.mov',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': context,
        }


    def restore_omna_stock(self):
        adjustment = self.count_on_hand - self.previous_quantity
        data = {"data": {"quantity": -1 * adjustment}}
        self.post('stock/items/%s' % (self.omna_id,), data)
        return self.write({'count_on_hand': self.previous_quantity})



    def reset_quantity(self, data):
        # https://cenit.io/app/ecapi-v1/stock/items
        # query_param = {'integration_id': self.integration_id.integration_id}
        # if self.product_template_omna_id:
        #     query_param.update({'product_id': self.product_template_omna_id})
        # if self.product_product_omna_id:
        #     query_param.update({'variant_id': self.product_product_omna_id})
        # response = self.get('stock/items', query_param)
        # qty = response.get('data')[0].get('count_on_hand')
        # omna_stock_item_id = response.get('data')[0].get('id')

        # https://cenit.io/app/ecapi-v1/stock/items/{stock_item_id}
        qty = self.count_on_hand
        to_reset = {"data": {"quantity": -1 * qty}}
        response = self.post('stock/items/%s' % (self.omna_id,), to_reset)
        response = self.post('stock/items/%s' % (self.omna_id,), data)
        self.write({'count_on_hand': data['data']['quantity']})


    # def _url_related_task(self):
    #     # http://localhost:8070/web#action=412&model=omna.task&view_type=list&cids=1&menu_id=256
    #     # http://localhost:8070/web#id=1-6266e5885a5a232b4800a7e4&action=412&model=omna.task&view_type=form&cids=1&menu_id=256
    #     link = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + \
    #            '/web#action=' + str(self.env.ref('ecapi_mercado_libre.action_omna_task').id) + \
    #            '&model=omna.task&view_type=list&cids=1&menu_id=' + str(self.env.ref('ecapi_mercado_libre.menu_omna_my_tasks').id)
    #     self.url_related_task = link



class StockMoveLine(models.Model):
    _name = "stock.move.line"
    _inherit = ['stock.move.line', 'omna.api']


    def write(self, vals):
        result = super(StockMoveLine, self).write(vals)

        for res in result:
            if res.product_id.product_tmpl_id.integration_ids and res.product_id.product_tmpl_id.integration_linked_ids and res.product_id.product_tmpl_id.omna_product_id:
                data = {"data": {"quantity": int(res.qty_done)}}
                # integration_id = res.location_dest_id.integration_id.integration_id if res.location_dest_id.omna_id else res.location_id.integration_id.integration_id
                integration_id = res.product_id.product_tmpl_id.integration_linked_ids.integration_id
                omna_product_id = res.product_id.omna_product_id
                omna_variant_id = res.product_id.omna_variant_id

                query_param = {'integration_id': integration_id}
                if omna_product_id:
                    query_param.update({'product_id': omna_product_id})
                if omna_variant_id:
                    query_param.update({'variant_id': omna_variant_id})
                # query_result = self.get('stock/items', query_param)
                # qty = response.get('data')[0].get('count_on_hand')
                # omna_stock_item_id = query_result.get('data')[0].get('id')
                # omna_stock_item_result = self.search([('omna_id', '=', omna_stock_item_id), ('integration_id.integration_id', '=', integration_id)])
                omna_stock_item_result = self.env['omna.stock.items'].search(['|', ('product_template_omna_id', '=', omna_product_id), ('product_product_omna_id', '=', omna_variant_id)])

                if (res.picking_id.picking_type_id.code == 'incoming'):
                    data['data']['quantity'] = int(1 * res.qty_done)
                    response1 = self.post('stock/items/%s' % (omna_stock_item_result.omna_id,), data)
                    aux = omna_stock_item_result.count_on_hand
                    omna_stock_item_result.write({'count_on_hand': aux + data['data']['quantity']})
                if (res.picking_id.picking_type_id.code == 'outgoing'):
                    data['data']['quantity'] = int(-1 * res.qty_done)
                    response2 = self.post('stock/items/%s' % (omna_stock_item_result.omna_id,), data)
                    aux = omna_stock_item_result.count_on_hand
                    omna_stock_item_result.write({'count_on_hand': aux + data['data']['quantity']})
                if not (res.picking_id.picking_type_id.code):
                    omna_stock_item_result.reset_quantity(data)

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





