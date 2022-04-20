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

import logging
from datetime import datetime, timezone, time
from odoo import models, api, exceptions
from dateutil.parser import parse

_logger = logging.getLogger(__name__)

STATUS_OMNA_MAPPER = {'Canceled': 'cancel', 'Payment accepted': 'payment_accepted', 'Payment error': 'payment_error', 'Pedido Preparado': 'prepared_order'}



class OmnaOrderMixin(models.AbstractModel):
    """
       Model for import orders utilities
    """
    _name = "omna.order.mixin"
    _description = "Omna Order Mixin"

    def sync_orders(self, orders):
        try:
            for order in orders:
                if order['status'] == 'Payment accepted':
                    # if order['status'] != False:

                    line_items = [X for X in order.get('original_raw_data').get('associations').get('order_rows')]

                    act_order = self.env['sale.order'].search([('omna_id', '=', order.get('id'))])
                    if act_order:
                        # Updating the order
                        data = {
                            'omna_order_reference': order.get('number'),
                            'state': STATUS_OMNA_MAPPER[order.get('status')]
                            # TODO Map OMNA order's states with sale order's states
                        }
                        act_order.write(data)

                        # Updating las order lines
                        # for line_item in order.get('line_items'):
                        for line_item in line_items:
                            act_orderline = self.env['sale.order.line'].search([('omna_id', '=', line_item.get('id'))])
                            product = self.env['product.product'].search([('default_code', '=', line_item.get('product_reference'))],
                                                                         limit=1)
                            if not act_orderline:
                                self._create_orderline(act_order, line_item, order.get('currency'))
                            #     data = {}
                            #     data.update({'price_unit': line_item.get('product_price')} if product else {})
                            #     data.update({'product_id': product.id} if product else {})
                            #     data.update({'name': product.product_tmpl_id.name} if product else {})
                            #     data.update({'product_uom': product.product_tmpl_id.uom_id.id} if product else {})
                            #     data.update({'product_uom_qty': line_item.get('product_quantity')} if product else {})
                            #
                            #     if not product.id:
                            #         data['display_type'] = 'line_section'
                            #
                            #     act_orderline.write(data)
                            # else:
                            #     self._create_orderline(act_order, line_item, order.get('currency'))
                    else:

                        partner_invoice = self.env['res.partner'].search([('name', '=', '%s %s' % (
                            order.get('bill_address').get('first_name'), order.get('bill_address').get('last_name')))],
                                                                         limit=1)
                        if not partner_invoice:
                            partner_invoice = self._create_partner(order.get('bill_address'))

                        partner_shipping = self.env['res.partner'].search([('name', '=', '%s %s' % (
                            order.get('ship_address').get('first_name'), order.get('ship_address').get('last_name')))],
                                                                          limit=1)
                        if not partner_shipping:
                            partner_shipping = self._create_partner(order.get('ship_address'))

                        if order.get('integration'):
                            integration = self.env['omna.integration'].search(
                                [('integration_id', '=', order.get('integration').get('id'))], limit=1)

                            if integration:

                                data = {
                                    'omna_id': order.get('id'),
                                    'integration_id': integration.id,
                                    'omna_order_reference': order.get('number'),
                                    'origin': 'OMNA',
                                    'state': 'draft',
                                    # 'state': STATUS_OMNA_MAPPER[order.get('status')],
                                    'amount_total': order.get('total_price'),
                                    # 'amount_total': '22.5',
                                    'date_order': parse(order.get('last_import_date').split('T')[0]),
                                    'create_date': datetime.now(timezone.utc),
                                    'partner_id': partner_invoice.id,
                                    'partner_invoice_id': partner_invoice.id,
                                    'partner_shipping_id': partner_shipping.id,
                                    'pricelist_id': self.env['product.pricelist'].search(
                                        [('name', '=', 'Public Pricelist'), ('active', '=', True)], limit=1).id,

                                }
                                if order.get('omna_tenant_id'):
                                    data['omna_tenant_id'] = order.get('omna_tenant_id')

                                omna_order = self.env['sale.order'].create(data)

                                # Creating the orderlines
                                # for line_item in order.get('line_items'):
                                for line_item in line_items:
                                    # self._create_orderline(omna_order, line_item, order.get('payments')[0].get('currency'))
                                    self._create_orderline(omna_order, line_item, order.get('currency'))

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)

    def _create_partner(self, address):
        data = {
            'name': '%s %s' % (address.get('first_name'), address.get('last_name')),
            'type': 'contact',
            'street': ' '.join(address.get('address')),
            'city': address.get('city'),
            'zip': address.get('zip_code'),
        }
        country = self.env['res.country'].search([('code', '=', address.get('country'))], limit=1)
        if country:
            state_manager = self.env['res.country.state']
            data['country_id'] = country.id
            state = state_manager.search(
                [('code', '=', address.get('state')), ('country_id', '=', country.id)], limit=1)
            if state:
                data['state_id'] = state.id
        return self.env['res.partner'].create(data)

    def _create_orderline(self, omna_order, line_item, currency):
        currency = self.env['res.currency'].search([('name', '=', currency)], limit=1)
        if not currency:
            currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)

        product = self.env['product.product'].search([('default_code', '=', line_item.get('product_reference'))], limit=1)
        # product = self.env['product.template'].search([('list_price', '=', line_item.get('price'))], limit=1)

        data = {
            'order_id': omna_order.id,
            'omna_id': line_item.get('id'),
            # 'name': product.product_tmpl_id.name if product else line_item.get('name'),
            'name': line_item.get('product_name'),
            'price_unit': line_item.get('product_price'),
            'state': omna_order.state,
            'product_id': product.id if product else False,
            # 'product_id': None,
            'product_uom': product.product_tmpl_id.uom_id.id if product else self.env.ref('uom.product_uom_unit').id,
            'product_uom_qty': line_item.get('product_quantity'),
            'customer_lead': 0,  #
            'currency_id': currency.id
        }

        if not product.id:
            data['display_type'] = 'line_section'

        self.env['sale.order.line'].create(data)
