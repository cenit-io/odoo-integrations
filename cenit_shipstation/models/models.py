# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010, 2014 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import models, fields, api, _


class ShipstationCarrier(models.Model):
    _name = 'shipstation.carrier'

    name = fields.Char('name')
    account_number = fields.Char('Account Number')
    carrier_code = fields.Char('Carrier Code')
    balance = fields.Float('Balance')

    def _import_carriers(self, data):
        for record in data:
            if not self.search(
                    [('account_number', '=', data['accountNumber'])]):
                self.create({'name': record['name'],
                             'account_number': record['accountNumber'],
                             'carrier_code': record['code'],
                             'balance': record['balance']})


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection([('shipstation', 'Shipstation')])
    shipstation_carrier_id = fields.Many2one('shipstation.carrier', 'Carrier')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def sync_orders(self, data):
        for record in data['shipments']:
            order = self.search(
                [('name', '=', record['orderNumber'])])
            if order and order.state != 'cancel':
                order.picking_ids.filtered(
                    lambda x: x.state != 'cancel').write(
                    {'carrier_tracking_ref': record['trackingNumber']})
