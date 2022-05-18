# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, exceptions, tools, _
from datetime import datetime, timezone, time
from dateutil.parser import parse

_logger = logging.getLogger(__name__)


class OmnaSyncOrders(models.TransientModel):
    _name = 'omna.sync_orders_wizard'
    _inherit = 'omna.api'

    sync_type = fields.Selection([('all', 'All'),
                                  ('by_integration', 'By Integration'),
                                  ('number', 'Number')], 'Import Type', required=True, default='all', help="If you select Number option, you have to provide the Reference value of an Order in Mercado Libre.")
    integration_id = fields.Many2one('omna.integration', 'Integration', domain=lambda self:[('company_id', '=', self.env.company.id)])
    number = fields.Char("Order Number")


    def sync_orders(self):
        try:
            limit = 100
            offset = 0
            requester = True
            orders = []

            prod_list = self.env['product.template'].search([])
            var_list = self.env['product.product'].search([])

            if not (prod_list and var_list):
                self.env.user.notify_channel('danger', _(
                    "Lo sentimos, pero no es posible realizar la importacion de ordenes. \n Por favor importe primero los productos, para luego proceder con la importacion de ordenes."),
                                             _("Error"), True)
                return

            if self.sync_type != 'number':
                while requester:
                    if self.sync_type == 'all':
                        response = self.get('orders', {'limit': limit, 'offset': offset, 'with_details': True})
                    else:
                        response = self.get('integrations/%s/orders' % self.integration_id.integration_id, {'limit': limit, 'offset': offset, 'with_details': True})
                    data = response.get('data')
                    orders.extend(data)
                    if len(data) < limit:
                    # if offset >= 5:
                        requester = False
                    else:
                        offset += limit
            else:
                response = self.get('integrations/%s/orders/%s' % (self.integration_id.integration_id, self.number), {'with_details': True})
                data = response.get('data')
                orders.append(data)

            if orders:
                self.do_import(orders)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload'
                }
            else:
                self.env.user.notify_channel('warning', _("Sorry, we don't find results for this criteria. \n Please execute from Settings / Import Mercado Libre -> Ecapi the option for import Orders, later try to execute this functionality."), _("Information"), True)

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)


    def do_import(self, orders):
        try:
            for order in orders:
                if order['status']:
                    line_items = order.get('line_items')

                    act_order = self.env['sale.order'].search([('omna_id', '=', order.get('id'))])
                    with_error = False

                    if not act_order:
                        partner_related = self._create_partner(order.get('customer'), contact_type='contact')
                        partner_shipping  = self._create_partner(order.get('ship_address'), contact_type='delivery')
                        partner_invoice = self._create_partner(order.get('bill_address'), contact_type='invoice')

                        if order.get('integration'):
                            integration = self.env['omna.integration'].search([('integration_id', '=', order.get('integration').get('id'))], limit=1)
                            warehouse_delivery = self.env['stock.warehouse'].sudo().search([('company_id', '=', integration.company_id.id), ('integration_id', '=', integration.id)])
                            payment_list = [(0, 0, {'currency': X.get('currency_id'), 'payment_method': X.get('payment_method'),
                                     'payment_ml_id': str(X.get('id')), 'total_paid_amount': X.get('total_paid_amount'), 'integration_id': integration.id, 'status': X.get('status')})for X in order.get('original_raw_data').get('payments')]
                            if integration:

                                data = {
                                    'omna_id': order.get('id'),
                                    'integration_id': integration.id,
                                    'omna_order_reference': order.get('number'),
                                    'omna_remote_state': order.get('status'),
                                    'origin': 'CENIT',
                                    'state': 'draft',
                                    'amount_total': round(float(order.get('total_price'))) ,
                                    # 'amount_total': '22.5',
                                    'date_order': fields.Datetime.to_string(parse(order.get('last_import_date').split('T')[0])),
                                    'create_date': fields.Datetime.to_string(datetime.now(timezone.utc)),
                                    'partner_id': partner_related.id,
                                    'partner_invoice_id': partner_invoice.id if partner_invoice else False,
                                    'partner_shipping_id': partner_shipping.id if partner_shipping else False,
                                    'warehouse_id': warehouse_delivery.id,
                                    'pricelist_id': self.env.ref('product.list0').id,
                                    'company_id': integration.company_id.id,

                                    'ship_first_name': order.get('ship_address').get('first_name') if order.get('ship_address', False) else False,
                                    'ship_last_name': order.get('ship_address').get('last_name') if order.get('ship_address', False) else False,
                                    'ship_country': order.get('ship_address').get('country') if order.get('ship_address', False) else False,
                                    'ship_state': order.get('ship_address').get('state') if order.get('ship_address', False) else False,
                                    'ship_city': order.get('ship_address').get('city') if order.get('ship_address', False) else False,
                                    'ship_district': order.get('ship_address').get('district') if order.get('ship_address', False) else False,
                                    'ship_town': order.get('ship_address').get('town') if order.get('ship_address', False) else False,
                                    'ship_phone': order.get('ship_address').get('phone') if order.get('ship_address', False) else False,
                                    'ship_zip_code': order.get('ship_address').get('zip_code') if order.get('ship_address', False) else False,
                                    'ship_address': ", ".join(order.get('ship_address').get('address')) if order.get('ship_address', False) else False,
                                    'bill_first_name': order.get('bill_address').get('first_name') if order.get('bill_address', False) else False,
                                    'bill_last_name': order.get('bill_address').get('last_name') if order.get('bill_address', False) else False,
                                    'bill_country': order.get('bill_address').get('country') if order.get('bill_address', False) else False,
                                    'bill_state': order.get('bill_address').get('state') if order.get('bill_address', False) else False,
                                    'bill_city': order.get('bill_address').get('city') if order.get('bill_address', False) else False,
                                    'bill_district': order.get('bill_address').get('district') if order.get('bill_address', False) else False,
                                    'bill_town': order.get('bill_address').get('town') if order.get('bill_address', False) else False,
                                    'bill_phone': order.get('bill_address').get('phone') if order.get('bill_address', False) else False,
                                    'bill_zip_code': order.get('bill_address').get('zip_code') if order.get('bill_address', False) else False,
                                    'bill_address': ", ".join(order.get('bill_address').get('address')) if order.get('bill_address', False) else False,
                                    'doc_type': order.get('original_raw_data').get('address_billing').get('billing_info').get('doc_type') if order.get('original_raw_data').get('address_billing', False) else False,
                                    'doc_number': order.get('original_raw_data').get('address_billing').get('billing_info').get('doc_number') if order.get('original_raw_data').get('address_billing', False) else False,
                                    'order_payment_ids': payment_list,

                                }
                                if order.get('omna_tenant_id'):
                                    data['omna_tenant_id'] = order.get('omna_tenant_id')

                                # omna_order = self.env['sale.order'].create(data)

                                # Creating the orderlines
                                # for line_item in order.get('line_items'):
                                aux = []
                                for line_item in line_items:
                                    # self._create_orderline(omna_order, line_item, order.get('payments')[0].get('currency'))
                                    temp_line = self._create_orderline(line_item, order.get('currency'))
                                    if temp_line:
                                        aux.append((0, 0, temp_line))
                                    if not temp_line:
                                        message = "La importacion de la orden # %s ha fallado. El producto: %s [%s], no se ha encontrado en el sistema." % (order.get('number'), line_item.get('name'), line_item.get('id'))
                                        self.env['ecapi.import.log'].create({'integration_id': self.integration_id.id, 'message': message})
                                        with_error = True


                                if not with_error:
                                    data['order_line'] = aux
                                    omna_order = self.env['sale.order'].create(data)

                                    amount_untaxed = amount_tax = 0.0
                                    for line in omna_order.order_line:
                                        amount_untaxed += line.price_subtotal
                                        amount_tax += line.price_tax
                                    omna_order.write({
                                        'amount_untaxed': amount_untaxed,
                                        'amount_tax': amount_tax,
                                        'amount_total': amount_untaxed + amount_tax,
                                    })
                                if with_error:
                                    pass
                                # omna_order._amount_all()

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)


    def _create_partner(self, dict_param, contact_type):
        if not dict_param:
            return False

        street =  "País: {0}, Estado: {1}, Ciudad: {2}, Distrito: {3}, Barrio/Localidad: {4}, ".format(dict_param.get('country') or '-',
                dict_param.get('state') or '-', dict_param.get('city') or '-', dict_param.get('district') or '-', dict_param.get('town') or '-')
        street += ", ".join(dict_param.get('address', []))
        data = {
            'name': '%s %s' % (dict_param.get('first_name'), dict_param.get('last_name')),
            'company_type': 'person',
            'type': contact_type,
            'email': dict_param.get('email'),
            'lang': self.env.user.lang,
            'integration_id': self.integration_id.id,
            'phone':  dict_param.get('phone'),
            'street':  street,
            'zip':  dict_param.get('zip_code'),
            # 'company_id':  self.integration_id.company_id.id
        }

        # data['country_id'] = self.env.ref('base.ar').id
        return self.env['res.partner'].create(data)


    def _create_orderline(self, line_item, currency):
        currency = self.env['res.currency'].search([('name', '=', currency)], limit=1)
        if not currency:
            currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)

        product = self.env['product.template'].search([('remote_product_id', '=', line_item.get('id'))], limit=1)
        if not product:
            return False

        data = {
            # 'order_id': omna_order.id,
            'omna_id': line_item.get('id'),
            'name': product.name if product else line_item.get('name'),
            # 'name': line_item.get('name'),
            'price_unit': product.list_price if product else line_item.get('price'),
            # 'price_unit': line_item.get('price'),
            # 'state': omna_order.state,
            'state': "draft",
            'qty_delivered_manual': 0,
            'product_id': product.product_variant_id.id if product else False,
            # 'product_id': False,
            'display_type': False,
            'product_uom': product.uom_id.id if product else self.env.ref('uom.product_uom_unit').id,
            # 'product_uom': self.env.ref('uom.product_uom_unit').id,
            'product_uom_qty': line_item.get('quantity'),
            'customer_lead': 0,  #
            'currency_id': currency.id,
            'product_packaging': False,
            'discount': 0,
            'product_template_id': product.id if product else False,
            # 'product_template_id': False,
            'route_id': False,
            # 'tax_id': [[6, False, [56]]],
        }

        # if not product.id:
        #     data['display_type'] = 'line_section'

        return data


    def _create_carrier_cost(self, omna_order):
        currency = self.env['res.currency'].search([('name', '=', omna_order.get('currency'))], limit=1)
        if not currency:
            currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)

        product = self.env['product.template'].search([('omna_product_id', '=', omna_order.get('original_raw_data').get('id_carrier'))], limit=1)


        data = {
            'omna_id': omna_order.get('original_raw_data').get('id_carrier'),
            'name': product.product_variant_id.name,
            'price_unit': float(omna_order.get('original_raw_data').get('total_shipping')),
            'state': "draft",
            'qty_delivered_manual': 0,
            'product_id': product.product_variant_id.id if product else False,
            'display_type': False,
            'product_uom': product.uom_id.id if product else self.env.ref('uom.product_uom_unit').id,
            'product_uom_qty': 1,
            'customer_lead': 0,  #
            'currency_id': currency.id,
            'product_packaging': False,
            'discount': 0,
            'product_template_id': product.id,
            'route_id': False,
        }

        if not product.id:
            data['display_type'] = 'line_section'

        return data


    def background_import_orders(self):
        try:
            limit = 10
            offset = 0
            requester = True
            orders = []
            integration_result = self.env['omna.integration'].search([], limit=1)

            while requester:
                response = self.get('integrations/%s/orders' % integration_result.integration_id, {'limit': limit, 'offset': offset, 'with_details': True})
                data = response.get('data')
                orders.extend(data)
                if len(data) < limit:
                    requester = False
                else:
                    offset += limit

            if orders:
                self.do_import(orders)
                _logger.info('The task to import orders from Cenit to Odoo have been created, please go to "System\Tasks" to check out the task status.')
            else:
                _logger.info("Sorry, we don't find new order records for import to Odoo.")

        except Exception as e:
            _logger.error(e)
            # raise exceptions.AccessError(e)
        pass


