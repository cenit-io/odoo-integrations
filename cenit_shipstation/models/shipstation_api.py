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

import requests
import logging
import base64

from odoo import models, api, exceptions, _

_logger = logging.getLogger(__name__)


class ShipstationApi(models.AbstractModel):
    """
       Model to connect to Shipstation API
    """
    _name = "shipstation.api"
    _description = "Shipstation Api"

    @api.model
    def get(self, url):
        headers = self.get_headers()
        try:
            _logger.info("[GET] %s ? {%s}", url, headers)
            r = requests.get(url, headers=headers)

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(_(
                "Error trying to connect to Shipstation."))

        if 200 <= r.status_code < 300:
            return r.json()
            # return r.status_code
        try:
            error = r.json()
            _logger.error(error)
        except Exception as e:
            _logger.error(e)
            _logger.info("\n\n%s\n", r.content)
            raise exceptions.ValidationError(_(
                "Shipstation returned with errors"))

        if 400 <= error.get('code', 400) < 500:
            raise exceptions.AccessError(_(
                "Error trying to connect to Shipstation."))

        raise exceptions.ValidationError(_("Shipstation returned with errors"))

    def get_headers(self):
        key = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_cenit.shipstation.key')
        secret = self.env['ir.config_parameter'].sudo().get_param(
            'odoo_cenit.shipstation.secret')
        basic = base64.b64encode(bytes(key + ':' + secret, 'utf-8')).decode(
            "utf-8")
        return {'Content-Type': 'application/json',
                'Authorization': 'Basic %s' % basic}
