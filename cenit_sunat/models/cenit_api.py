# -*- coding: utf-8 -*-
# #############################################################################
#
# OpenERP, Open Source Management Solution
# Copyright (C) 2004-2010, 2014 Tiny SPRL (<http://tiny.be>).
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


import requests
import simplejson
import logging

from openerp import models, api, exceptions
from cenit_base import CenitApi

import json

_logger = logging.getLogger(__name__)

API_PATH = "/api/v1"


class CenitApiSunat(models.AbstractModel):
    _name = 'cenit.api.sunat'
    _inherit = 'cenit.api'

    def post(self, path, vals):
            config = self.instance()

            payload = simplejson.dumps(vals)
            url = config.get('cenit_url') + API_PATH + path
            headers = self.headers(config)

            try:
                _logger.info("[POST] %s ? %s {%s}", url, payload, headers)
                r = requests.post(url, data=payload, headers=headers)
            except Exception as e:
                _logger.error(e)
                raise exceptions.AccessError("Error trying to connect to Cenit.")
            if 200 <= r.status_code < 300:
                if r.text != '':
                    text = json.loads(r.text)
                    if 'errors' in text:
                        errors_list = text['errors'].itervalues().next()['errors']
                        msg = ""
                        for e in errors_list:
                            if msg == "":
                                msg = e
                            else:
                                msg = msg + ', ' + e
                        raise exceptions.ValidationError("There are errors in document sent: "+ msg)
                return r.json()

            try:
                error = r.json()
                _logger.error(error)
            except Exception as e:
                _logger.error(e)
                raise exceptions.ValidationError("Cenit returned with errors")

            if 400 <= error.get('code', 400) < 500:
                raise exceptions.AccessError("Error trying to connect to Cenit.")

            raise exceptions.ValidationError("Cenit returned with errors")

    CenitApi.post = post


