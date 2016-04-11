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

from openerp import models, fields, exceptions


_logger = logging.getLogger(__name__)

COLLECTION_NAME = "ublpe"
COLLECTION_VERSION = "0.1.1"
COLLECTION_PARAMS = {}


class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.ublpe.settings"
    _inherit = 'res.config.settings'

    ############################################################################
    # Pull Parameters
    ############################################################################
    #key = fields.Char('Shipstation Key')
    #secret = fields.Char('Shipstation Secret')

    ############################################################################
    # Default Getters
    ############################################################################
    '''
    def get_default_key(self, cr, uid, ids, context=None):
        key = self.pool.get('ir.config_parameter').get_param(
            cr, uid,
            'odoo_cenit.shipstation.key', default=None,
            context=context
        )
        return {'key': key or ''}

    def get_default_secret(self, cr, uid, ids, context=None):
        secret = self.pool.get('ir.config_parameter').get_param(
            cr, uid,
            'odoo_cenit.shipstation.secret', default=None,
            context=context
        )
        return {'secret': secret or ''}
    
    ############################################################################
    # Default Setters
    ############################################################################
    def set_key(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid,
                'odoo_cenit.shipstation.key', record.key or '',
                context=context
            )
    
    def set_secret(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid,
                'odoo_cenit.shipstation.secret', record.secret or '',
                context=context
            )
    '''

    ############################################################################
    # Actions
    ############################################################################
    def install(self, cr, uid, context=None):

        installer = self.pool.get('cenit.collection.installer')
        data = installer.get_collection_data(
            cr, uid,
            COLLECTION_NAME,
            version=COLLECTION_VERSION,
            context=context
        )

        params = {}
        '''
        for p in data.get('params'):
            k = p.get('key')
            id_ = p.get('id')
            value = getattr(obj, COLLECTION_PARAMS.get(k, k))
            params.update({id_: value})
        '''
        installer.install_collection(
            cr, uid,
            data.get('id'),
            params=params,
            context=context
        )

        # rc2 = self.post_install(cr, uid, context=context)
        # if not rc2:
        #     raise exceptions.AccessError("Something went wrong")

