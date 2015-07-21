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

from openerp import models, fields


_logger = logging.getLogger(__name__)

COLLECTION_NAME = "twilio"
COLLECTION_VERSION = "1.0.0"
COLLECTION_PARAMS = {
    "On connection 'Twilio API Conection' template parameter 'account_sid'":'account_sid',
    "On connection 'Twilio API Conection' template parameter 'auth_token'":'auth_token',
}


class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.twilio.settings"
    _inherit = 'res.config.settings'

    ############################################################################
    # Pull Parameters
    ############################################################################
    account_sid = fields.Char('Account SID')
    auth_token = fields.Char('Auth Token')

    ############################################################################
    # Default Getters
    ############################################################################
    def get_default_account_sid(self, cr, uid, ids, context=None):
        account_sid = self.pool.get('ir.config_parameter').get_param(
            cr, uid,
            'odoo_cenit.twilio.account_sid', default=None,
            context=context
        )
        return {'account_sid': account_sid or ''}
    
    def get_default_auth_token(self, cr, uid, ids, context=None):
        auth_token = self.pool.get('ir.config_parameter').get_param(
            cr, uid,
            'odoo_cenit.twilio.auth_token', default=None,
            context=context
        )
        return {'auth_token': auth_token or ''}
    
    ############################################################################
    # Default Setters
    ############################################################################
    def set_account_sid(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid,
                'odoo_cenit.twilio.account_sid', record.account_sid or '',
                context=context
            )
    
    def set_auth_token(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid,
                'odoo_cenit.twilio.auth_token', record.auth_token or '',
                context=context
            )
    
    ############################################################################
    # Actions
    ############################################################################
    def execute(self, cr, uid, ids, context=None):
        rc = super(CenitIntegrationSettings, self).execute(
            cr, uid, ids, context=context
        )

        if not context.get('install', False):
            return rc

        objs = self.browse(cr, uid, ids)
        if not objs:
            return rc
        obj = objs[0]

        installer = self.pool.get('cenit.collection.installer')
        data = installer.get_collection_data(
            cr, uid,
            COLLECTION_NAME,
            version = COLLECTION_VERSION,
            context = context
        )

        params = {}
        for p in data.get('params'):
            k = p.get('parameter')
            id_ = p.get('id')
            value = getattr(obj,
                COLLECTION_PARAMS.get(k)
            )
            params.update ({
                id_: value
            })

        installer.install_collection(
            cr, uid,
            data.get('id'),
            params = params,
            context = context
        )

        return rc
