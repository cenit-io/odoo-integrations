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

from openerp import models, fields, api


_logger = logging.getLogger(__name__)

COLLECTION_NAME = "oasis_supplier"
COLLECTION_VERSION = "0.1.0"
COLLECTION_PARAMS = {
    'Username':'username',
    'Password':'password',
}

class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.oasis_supplier.settings"
    _inherit = 'res.config.settings'

    ############################################################################
    # Pull Parameters
    ############################################################################
    username = fields.Char('Username')
    password = fields.Char('Password')

    ############################################################################
    # Default Getters
    ############################################################################
    def get_default_username(self, context):
        username = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.oasis_supplier.username', default=None
        )
        return {'username': username or ''}

    def get_default_password(self, context):
        password = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.oasis_supplier.password', default=None
        )
        return {'password': password or ''}


    ############################################################################
    # Default Setters
    ############################################################################
    def set_username(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.oasis_supplier.username', record.username or ''
            )

    def set_password(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.oasis_supplier.password', record.password or ''
            )


    ############################################################################
    # Actions
    ############################################################################
    def execute(self):
        rc = super(CenitIntegrationSettings, self).execute()

        if not self.env.context.get('install', False):
            return rc

        objs = self.browse(self.ids)
        if not objs:
            return rc
        obj = objs[0]

        installer = self.env['cenit.collection.installer']
        data = installer.get_collection_data(
            COLLECTION_NAME,
            version = COLLECTION_VERSION
        )

        params = {}
        for p in data.get('pull_parameters'):
            k = p['label']
            id_ = p.get('id')
            value = getattr(obj,COLLECTION_PARAMS.get(k))
            params.update ({id_: value})

        installer.pull_shared_collection(data.get('id'), params=params)
        installer.install_common_data(data['data'])

        return rc
