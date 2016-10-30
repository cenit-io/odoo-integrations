import logging
from openerp import http
from openerp.addons.cenit_base.controllers.main import WebhookController
from openerp.http import request
from openerp import SUPERUSER_ID
from openerp.modules.registry import RegistryManager
import json


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
                    return r  # TODO investigar  tipo de codigo q se devuelve en caso de eror en los datos
            else:
                status_code = 404

        return {'status': status_code}

    def create_order(self, cr, request):
        order_data = request.jsonrequest
        partner_name = order_data['partner_id']['name']
        context = request.context

        partner_id = self.get_id_from_record(cr, 'res.partner', [('name', '=', partner_name)], context=context)
        if partner_id:
            order_data['partner_id'] = partner_id  # Updating partner_id(Customer)
            order_data['partner_invoice_id'] = partner_id  # Updating invoice address
            order_data['partner_shipping_id'] = partner_id  # Updating shipping address

            order_data['payment_term'] = self.get_id_from_record(cr, 'account.payment.term',
                                                                 [('name', '=', order_data['payment_term'])],
                                                                 context=context)

            order_data['warehouse_id'] = self.get_id_from_record(cr, 'stock.warehouse',
                                                                 [('name', '=', order_data['warehouse_id'])],
                                                                 context=context)

            order_data['user_id'] = self.get_id_from_record(cr, 'res.users', [('name', '=', order_data['user_id'])],
                                                            context=context)  # Updating sales person

            order_data['team_id'] = self.get_id_from_record(cr, 'crm.team', [('name', '=', order_data['team_id'])],
                                                            context=context)

            # Order lines
            orders = order_data['order_line']
            for order in orders:
                order['product_id'] = self.get_id_from_record(cr, 'product.product', [('name', '=', order['name'])],
                                                              context=context)
                #product = request.browse(cr, SUPERUSER_ID, order['product_id'], context=context )
                # TODO ver si tengo agregar la descripcion del producto, barcode, delivered, invoiced, unit price, taxes
            order_data['order_line'] = orders

            errors = None
            try:
                request.registry['sale.order'].create(cr, SUPERUSER_ID, order_data)
                print 'Creooooo orden'
            except Exception as e:
                _logger.error(e)
                errors = e

            #if not errors:
               #errors = self.create_invoice(cr, order_data, request)

            return {'errors': errors} if errors else None

        return {'errors:': 'There is no Customer named %s'(partner_name)}

    def get_id_from_record(self, cr, model, domain, context):
        i_registry = request.registry[model]
        rc = i_registry.search(cr, SUPERUSER_ID, domain, context=context)  # Returns id
        if rc:
            return rc[0]
        else:
            return None

    def create_invoice(self, cr, order, request):
        i_registry = request.registry['account.invoice']

        invoice_data = {}
        invoice_data['partner_id'] = order['partner_id']
        invoice_data['jmd_partner_shipping_id'] = order['partner_shipping_id']
        invoice_data['payment_term_id'] = order['payment_term']
        invoice_data['invoice_date'] = order['create_date']
        invoice_data['user_id'] = order['user_id']
        invoice_data['team_id'] = order['team_id']
        invoice_data['currency_id'] = 'SGD'

        journal_id = self.get_id_from_record(cr, 'account.journal', [('name', '=', 'Sales Journal')])
        invoice_data['journal_id'] = journal_id

        account_id = self.get_id_from_record(cr, 'account.account', [('name', '=', 'Trade Debtors')])
        invoice_data['account_id'] = account_id

        invoice_data['origin'] = order['name']
        # invoice_data['move_id'] OJO duda
        lines = []
        for ord in order['order_line']:
            line = {}
            line['product_id'] = ord['product_id']
            line['quantity'] = ord['']
            line['jmd_product_barcode'] = ord['jmd_product_barcode']
            lines.append(line)

        invoice_data['invoice_line_id'] = lines
        errors = ''
        try:
           i_registry.create(cr, SUPERUSER_ID, json.dumps(invoice_data))
        except Exception as e:
            _logger.error(e)
            errors = e

        return errors if errors else None

    @http.route(['/test/<string:action>',
                 '/test/<string:action>/<string:root>'],
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
                order = {'partner_id': 1, 'partner_invoice_id': 1, 'partner_shipping_id': 1}
                request.registry['sale.order'].create(cr, SUPERUSER_ID, order)