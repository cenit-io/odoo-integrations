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

COLLECTION_NAME = "magento_1_9"
COLLECTION_VERSION = "1.0.0"
COLLECTION_PARAMS = {
    'Magento host':'magentohost',
    'OAuth consumer key':'oauth_key',
    'OAuth Consumer Secret':'oauth_secret',
}

class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.magento_1_9.settings"
    _inherit = 'res.config.settings'

    ############################################################################
    # Pull Parameters
    ############################################################################
    magentohost = fields.Char('Magento host')
    oauth_key = fields.Char('OAuth consumer key')
    oauth_secret = fields.Char('OAuth Consumer Secret')

    ############################################################################
    # Default Getters
    ############################################################################
    def get_default_magentohost(self, context):
        magentohost = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.magento_1_9.magentohost', default=None
        )
        return {'magentohost': magentohost or ''}

    def get_default_oauth_key(self, context):
        oauth_key = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.magento_1_9.oauth_key', default=None
        )
        return {'oauth_key': oauth_key or ''}

    def get_default_oauth_secret(self, context):
        oauth_secret = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.magento_1_9.oauth_secret', default=None
        )
        return {'oauth_secret': oauth_secret or ''}


    ############################################################################
    # Default Setters
    ############################################################################
    def set_magentohost(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.magento_1_9.magentohost', record.magentohost or ''
            )

    def set_oauth_key(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.magento_1_9.oauth_key', record.oauth_key or ''
            )

    def set_oauth_secret(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.magento_1_9.oauth_secret', record.oauth_secret or ''
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
