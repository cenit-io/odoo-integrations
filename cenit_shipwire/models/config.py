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

COLLECTION_NAME = "shipwire"
COLLECTION_VERSION = "1.0.0"
COLLECTION_PARAMS = {
    "On connection 'ShipWire Connection' template parameter 'shipwire_username'":'shipwire_username',
    "On connection 'ShipWire Connection' template parameter 'shipwire_password'":'shipwire_password',
}


class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.shipwire.settings"
    _inherit = 'res.config.settings'

    ############################################################################
    # Pull Parameters
    ############################################################################
    shipwire_username = fields.Char('Username')
    shipwire_password = fields.Char('Password')

    ############################################################################
    # Default Getters
    ############################################################################
    def get_default_shipwire_username(self, cr, uid, ids, context=None):
        shipwire_username = self.pool.get('ir.config_parameter').get_param(
            cr, uid,
            'odoo_cenit.shipwire.shipwire_username', default=None,
            context=context
        )
        return {'shipwire_username': shipwire_username or ''}
    
    def get_default_shipwire_password(self, cr, uid, ids, context=None):
        shipwire_password = self.pool.get('ir.config_parameter').get_param(
            cr, uid,
            'odoo_cenit.shipwire.shipwire_password', default=None,
            context=context
        )
        return {'shipwire_password': shipwire_password or ''}
    
    ############################################################################
    # Default Setters
    ############################################################################
    def set_shipwire_username(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid,
                'odoo_cenit.shipwire.shipwire_username', record.shipwire_username or '',
                context=context
            )
    
    def set_shipwire_password(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid,
                'odoo_cenit.shipwire.shipwire_password', record.shipwire_password or '',
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
