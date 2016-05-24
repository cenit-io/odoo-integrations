# -*- coding: utf-8 -*-

import logging
import inflect

from openerp import http
from openerp import SUPERUSER_ID
from openerp.http import request
from openerp.modules.registry import RegistryManager


_logger = logging.getLogger(__name__)


class SunatWebhookController(http.Controller):

    @http.route(['/sunat/<string:action>',
                 '/sunat/<string:action>/<string:root>'],
                type='json', auth='none', methods=['POST'])
    def cenit_sunat_post(self, action, root=None):
        status_code = 400
        environ = request.httprequest.headers.environ.copy()

        key = environ.get('HTTP_X_USER_ACCESS_KEY', False)
        token = environ.get('HTTP_X_USER_ACCESS_TOKEN', False)
        db_name = environ.get('HTTP_TENANT_DB', False)

        if not db_name:
            host = environ.get('HTTP_HOST', "")
            db_name = host.replace(".", "_").split(":")[0]

        # if db_name in http.db_list():
        registry = RegistryManager.get(db_name)
        with registry.cursor() as cr:
            connection_model = registry['cenit.connection']
            domain = [('key', '=', key), ('token', '=', token)]
            _logger.info(
                "Searching for a cenit.connection")
            rc = connection_model.search(cr, SUPERUSER_ID, domain)
            _logger.info("Candidate connections: %s", rc)

            if rc:
                if 'dataType' in request.jsonrequest:
                    if request.jsonrequest['dataType'] == 'DocumentHeader':
                        document = request.jsonrequest['data']


                        domain = [('number', '=', document['documentName'])]

                        context = request.context
                        invoice = request.registry['account.invoice'].search(cr, SUPERUSER_ID, domain, context=context)

                        if invoice:
                            email_data = {
                                'type': 'email',
                                'body': document['responseDescription'],
                                'model': 'account.invoice',
                                'res_id': invoice[0],
                                'record_name': document['documentName']
                            }
                            email = request.registry['mail.message'].create(cr, SUPERUSER_ID, email_data)

                            request.registry['account.invoice'].write(cr, SUPERUSER_ID, invoice,
                                                                      {'document_state_sunat': document['state']}, context=context)

                status_code = 200
            else:
                status_code = 404

        return {'status': status_code}


class HandleResponses:
    def __init__(self):
        pass

    def post_document_header_to_account_invoice(self, cr, SUPERUSER_ID, document):
        pass
