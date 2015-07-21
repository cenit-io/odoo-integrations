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

COLLECTION_NAME = "twitter"
COLLECTION_VERSION = "1.0.0"
COLLECTION_PARAMS = {
    "On connection 'Twitter API Connection' template parameter 'consumer_key'":'consumer_key',
    "On connection 'Twitter API Connection' template parameter 'consumer_secret'":'consumer_secret',
    "On connection 'Twitter API Connection' template parameter 'oauth_token'":'oauth_token',
    "On connection 'Twitter API Connection' template parameter 'oauth_token_secret'":'oauth_token_secret',
}


class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.twitter.settings"
    _inherit = 'res.config.settings'

    ############################################################################
    # Pull Parameters
    ############################################################################
    consumer_key = fields.Char('Consumer Key')
    consumer_secret = fields.Char('Consumer Secret')
    oauth_token = fields.Char('Oauth Token')
    oauth_token_secret = fields.Char('Oauth Token Secret')

    ############################################################################
    # Default Getters
    ############################################################################
    def get_default_consumer_key(self, cr, uid, ids, context=None):
        consumer_key = self.pool.get('ir.config_parameter').get_param(
            cr, uid,
            'odoo_cenit.twitter.consumer_key', default=None,
            context=context
        )
        return {'consumer_key': consumer_key or ''}
    
    def get_default_consumer_secret(self, cr, uid, ids, context=None):
        consumer_secret = self.pool.get('ir.config_parameter').get_param(
            cr, uid,
            'odoo_cenit.twitter.consumer_secret', default=None,
            context=context
        )
        return {'consumer_secret': consumer_secret or ''}
    
    def get_default_oauth_token(self, cr, uid, ids, context=None):
        oauth_token = self.pool.get('ir.config_parameter').get_param(
            cr, uid,
            'odoo_cenit.twitter.oauth_token', default=None,
            context=context
        )
        return {'oauth_token': oauth_token or ''}
    
    def get_default_oauth_token_secret(self, cr, uid, ids, context=None):
        oauth_token_secret = self.pool.get('ir.config_parameter').get_param(
            cr, uid,
            'odoo_cenit.twitter.oauth_token_secret', default=None,
            context=context
        )
        return {'oauth_token_secret': oauth_token_secret or ''}
    
    ############################################################################
    # Default Setters
    ############################################################################
    def set_consumer_key(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid,
                'odoo_cenit.twitter.consumer_key', record.consumer_key or '',
                context=context
            )
    
    def set_consumer_secret(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid,
                'odoo_cenit.twitter.consumer_secret', record.consumer_secret or '',
                context=context
            )
    
    def set_oauth_token(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid,
                'odoo_cenit.twitter.oauth_token', record.oauth_token or '',
                context=context
            )
    
    def set_oauth_token_secret(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid,
                'odoo_cenit.twitter.oauth_token_secret', record.oauth_token_secret or '',
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
