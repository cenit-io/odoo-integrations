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

COLLECTION_NAME = "desk"
COLLECTION_VERSION = "1.0.0"
COLLECTION_PARAMS = {
    "On connection 'Desk Connection' template parameter 'desk_url'":'desk_url',
    "On connection 'Desk Connection' template parameter 'desk_username'":'desk_username',
    "On connection 'Desk Connection' template parameter 'desk_password'":'desk_password',
}

class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.desk.settings"
    _inherit = 'res.config.settings'

    ############################################################################
    # Pull Parameters
    ############################################################################
    desk_url = fields.Char('Desk URL')
    desk_username = fields.Char('Desk Username')
    desk_password = fields.Char('Desk Password')

    ############################################################################
    # Default Getters
    ############################################################################
    def get_default_desk_url(self, cr, uid, ids, context=None):
        desk_url = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'odoo_cenit.desk.desk_url', default=None, context=context
        )
        return {'desk_url': desk_url or ''}

    def get_default_desk_username(self, cr, uid, ids, context=None):
        desk_username = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'odoo_cenit.desk.desk_username', default=None, context=context
        )
        return {'desk_username': desk_username or ''}

    def get_default_desk_password(self, cr, uid, ids, context=None):
        desk_password = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'odoo_cenit.desk.desk_password', default=None, context=context
        )
        return {'desk_password': desk_password or ''}


    ############################################################################
    # Default Setters
    ############################################################################
    def set_desk_url(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid, 'odoo_cenit.desk.desk_url', record.desk_url or '',
                context=context
            )

    def set_desk_username(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid, 'odoo_cenit.desk.desk_username', record.desk_username or '',
                context=context
            )

    def set_desk_password(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid, 'odoo_cenit.desk.desk_password', record.desk_password or '',
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
            value = getattr(obj,COLLECTION_PARAMS.get(k))
            params.update ({id_: value})

        installer.pull_shared_collection(cr, uid, data.get('id'), params=params, context=context)

        return rc
