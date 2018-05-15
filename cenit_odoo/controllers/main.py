__author__ = 'mary'

import logging
from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
from odoo.modules.registry import Registry

import json
from odoo.api import Environment

_logger = logging.getLogger(__name__)


class OdooController(http.Controller):

    @http.route(['/lead'],
                type='json', auth='none', methods=['POST'])
    def create_lead(self):
        """
          Creates a new lead
        """
        db_name = self.search_connection(request)
        registry = Registry(db_name)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            data = request.jsonrequest
            lead = env['crm.lead'].create(data)


    def search_connection(self, request):
        environ = request.httprequest.headers.environ.copy()

        key = environ.get('HTTP_X_USER_ACCESS_KEY', False)
        token = environ.get('HTTP_X_USER_ACCESS_TOKEN', False)
        db_name = environ.get('HTTP_TENANT_DB', False)

        if not db_name:
            host = environ.get('HTTP_HOST', "")
            db_name = host.replace(".", "_").split(":")[0]

        registry = Registry(db_name)
        with registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            connection_model = env['cenit.connection']
            domain = [('key', '=', key), ('token', '=', token)]
            _logger.info(
                "Searching for a 'cenit.connection' with key '%s' and "
                "matching token", key)
            rc = connection_model.search(domain)
            _logger.info("Candidate connections: %s", rc)
            if rc is not None:
                return db_name
            else:
                status_code = 404
        r = {'status': status_code}

        return json.dumps(r)