import logging
from openerp import http
from openerp.addons.cenit_base.controllers.main import WebhookController
from openerp.http import request
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
import json, simplejson
from datetime import datetime


_logger = logging.getLogger(__name__)


class MagentoController(WebhookController):
    '''
      Creates a sales order
    '''

    @http.route(['/orders/<string:action>',
                 '/orders/<string:action>/<string:root>'],
                type='json', auth='none', methods=['POST'])
    def create_sales_orders(self, action, root=None):
        status_code = 400
        environ = request.httprequest.headers.environ.copy()

        key = environ.get('HTTP_X_USER_ACCESS_KEY', False)
        token = environ.get('HTTP_X_USER_ACCESS_TOKEN', False)
        db_name = environ.get('HTTP_TENANT_DB', False)

        if not db_name:
            host = environ.get('HTTP_HOST', "")
            db_name = host.replace(".", "_").split(":")[0]

        registry = RegistryManager.get(db_name)
        with registry.cursor() as cr:
            connection_model = registry['cenit.connection']
            domain = [('key', '=', key), ('token', '=', token)]
            _logger.info(
                "Searching for a 'cenit.connection' with key '%s' and "
                "matching token", key)
            rc = connection_model.search(cr, SUPERUSER_ID, domain)
            _logger.info("Candidate connections: %s", rc)
            if rc:
                r = self.create_order(cr, request)
                if not r:
                    status_code = '200'
                else:
                    return r
            else:
                status_code = 404

        return {'status': status_code}

    def create_order(self, cr, request):
        order_data = json.dumps(request.jsonrequest)
        order_data = simplejson.loads(str(order_data.decode()))

        partner_name = order_data['partner_id']['name']
        context = request.context

        partner_id = self.get_id_from_record(cr, 'res.partner', [('name', '=', partner_name)], context=context)
        if partner_id:
            order_data['partner_id'] = partner_id  # Updating partner_id(Customer)
            order_data['partner_invoice_id'] = partner_id  # Updating invoice address
            order_data['partner_shipping_id'] = partner_id  # Updating shipping address

            order_data['payment_term_id'] = self.get_id_from_record(cr, 'account.payment.term',
                                                                    [('name', '=', order_data['payment_term_id'])],
                                                                    context=context)

            order_data['warehouse_id'] = self.get_id_from_record(cr, 'stock.warehouse',
                                                                 [('name', '=', order_data['warehouse_id'])],
                                                                 context=context)

            order_data['user_id'] = self.get_id_from_record(cr, 'res.users', [('name', '=', order_data['user_id'])],
                                                            context=context)  # Updating sales person

            order_data['team_id'] = self.get_id_from_record(cr, 'crm.team', [('name', '=', order_data['team_id'])],
                                                            context=context)
            order_data['invoice_status'] = 'invoiced'

            errors = None

            lines = {}
            if order_data.get('order_line'):
                lines = order_data.pop('order_line')
                saleorder_registry = request.registry['sale.order']
            try:
                order_id = self.get_id_from_record(cr, 'sale.order', [('name', '=', order_data.get('name'))], context=context)
                if not order_id:
                    order_id = saleorder_registry.create(cr, SUPERUSER_ID, order_data)
                else:
                    saleorder_registry.write(cr, SUPERUSER_ID, order_id, order_data)
                if order_id:
                    # Create order lines
                    if lines:
                        for line in lines:
                            line['product_id'] = self.get_id_from_record(cr, 'product.product',
                                                                         [('name', '=', line['name'])],
                                                                         context=context)
                            i_registry = request.registry['product.product']
                            # if not line['product_id']:
                            #     i_registry.create(cr, SUPERUSER_ID, )

                            product = i_registry.browse(cr, SUPERUSER_ID, line['product_id'], context=context)[0]
                            line['name'] = product['name']
                            line['order_id'] = order_id
                            line['product_uom'] = product['uom_id']['id']
                            line['price_unit'] = product['list_price']
                            line['customer_lead'] = product['sale_delay']

                            line['tax_id'] = [[x.id] for x in product['taxes_id']]
                            line['tax_id'] = [(6, False, line['tax_id'][0])]

                            line['property_account_income_id'] = product['property_account_income_id']['id']
                            line['property_account_expense_id'] = product['property_account_expense_id']['id']

                            line_id = self.get_id_from_record(cr, 'sale.order.line', [('order_id', '=', order_id),
                                                                                      ('product_id', '=', product['id'])], context=context)
                            if not line_id:
                                request.registry['sale.order.line'].create(cr, SUPERUSER_ID, line)
                            else:
                                request.registry['sale.order.line'].write(cr, SUPERUSER_ID, line_id, line)


            except Exception as e:
                _logger.error(e)
                errors = e

            if not errors:
                order_data['order_line'] = lines
                errors = self.create_invoice(cr, order_data, request, context)

            return {'errors': errors} if errors else None

        return {'errors:': 'There is no Customer named %s'(partner_name)}

    def get_id_from_record(self, cr, model, domain, context):
        i_registry = request.registry[model]
        rc = i_registry.search(cr, SUPERUSER_ID, domain, context=context)  # Returns id
        if rc:
            return rc[0]
        else:
            return None

    def create_invoice(self, cr, order, request, context):
        i_registry = request.registry['account.invoice']

        invoice_data = {}
        invoice_data['partner_id'] = order.get('partner_id', '')
        invoice_data['jmd_partner_shipping_id'] = order.get('partner_shipping_id', '')
        invoice_data['payment_term_id'] = order.get('payment_term_id', '')
        invoice_data['date_invoice'] = order.get('date_order', datetime.now())
        invoice_data['user_id'] = order.get('user_id', '')
        invoice_data['team_id'] = order.get('team_id', '')
        # invoice_data['currency_id'] = 'SGD'

        journal_id = self.get_id_from_record(cr, 'account.journal', [('name', '=', 'Sales Journal')], context=context)
        invoice_data['journal_id'] = journal_id

        account_id = self.get_id_from_record(cr, 'account.account', [('name', '=', 'Trade Debtors')], context=context)
        invoice_data['account_id'] = account_id

        invoice_data['origin'] = order.get('name', '')
        invoice_data['state'] = 'open'


        errors = ''
        try:
            invoice_id = self.get_id_from_record(cr, 'account.invoice', [('origin', '=', order.get('name'))], context=context)
            if not invoice_id:
               invoice_id = i_registry.create(cr, SUPERUSER_ID, invoice_data)
            else:
                 i_registry.write(cr, SUPERUSER_ID, invoice_id, invoice_data)

            if invoice_id:
                orderlines = order.get('order_line', {})
                for ord in orderlines:
                    ord['quantity'] = ord['product_uom_qty']
                    ord.pop('product_uom_qty')
                    ord['uom_id'] = ord['product_uom']
                    ord.pop('product_uom')
                    ord['invoice_line_tax_ids'] = ord['tax_id']
                    ord.pop('tax_id')
                    ord['invoice_id'] = invoice_id
                    ord['account_id'] = ord.get('property_account_income_id', 'property_account_expense_id')

                    line_id = self.get_id_from_record(cr, 'account.invoice.line', [('invoice_id', '=', invoice_id),
                                                                                   ('product_id', '=', ord['product_id'])], context=context)
                    if not line_id:
                        request.registry['account.invoice.line'].create(cr, SUPERUSER_ID, ord)
                    else:
                        request.registry['account.invoice.line'].write(cr, SUPERUSER_ID, line_id, ord)
        except Exception as e:
            _logger.error(e)
            errors = e


        return errors if errors else None