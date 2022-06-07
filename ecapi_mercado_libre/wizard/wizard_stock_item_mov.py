# -*- coding: utf-8 -*-
import json
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError
from odoo.exceptions import *


class WizardStockItemMov(models.TransientModel):
    _name = "wizard.stock.item.mov"
    _description = "Stock Item Movement"

    cantidad = fields.Integer(string="Cantidad a mano", default=lambda self: self._context.get('count_on_hand'))
    cantidad_movimiento = fields.Integer(string="Cantidad a mover", default=1)
    cantidad_resultante = fields.Integer(string="Cantidad resultante", compute='_cantidad_resultante')

    def update_quantity(self):
        self.ensure_one()
        data = {"data": {"quantity": self.cantidad_movimiento}}
        omna_stock_items = self.env['omna.stock.items']
        omna_stock_item_id = self.env.context.get('omna_stock_item_id')
        integration_id = self.env.context.get('integration_id')
        omna_product_id = self.env.context.get('omna_product_id')
        omna_variant_id = self.env.context.get('omna_variant_id')
        omna_stock_item_result = omna_stock_items.search([('omna_id', '=', omna_stock_item_id)])
        response = omna_stock_items.post('stock/items/%s' % (omna_stock_item_id,), data)
        aux = omna_stock_item_result.count_on_hand
        omna_stock_item_result.write({'count_on_hand': aux + self.cantidad_movimiento})
        link = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + \
               '/web#action=' + str(self.env.ref('ecapi_mercado_libre.action_omna_task').id) + \
               '&model=omna.task&view_type=list&cids=1&menu_id=' + str(
            self.env.ref('ecapi_mercado_libre.menu_omna_my_tasks').id)
        access_link = f'<a href="{link}" style="padding:2px;color:#56b3b5;font-weight:bold;text-decoration:none;">Access to this link</a>'
        self.env.user.notify_channel('info', _('Please check the task list to be sure of the process was done correctly.\n %s' % access_link), _("Information"), True)

    @api.depends('cantidad_movimiento')
    def _cantidad_resultante(self):
        self.cantidad_resultante = self.cantidad + self.cantidad_movimiento
