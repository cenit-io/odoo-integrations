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

COLLECTION_NAME = "geneea_natural_language_processing_1_0"
COLLECTION_VERSION = "0.1"
COLLECTION_PARAMS = {
    "On connection 'Geneea Natural Language Processing 1.0 Connection' template parameter 'api_key'":'api_key',
}

class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.geneea_natural_language_processing_1_0.settings"
    _inherit = 'res.config.settings'

    ############################################################################
    # Pull Parameters
    ############################################################################
    api_key = fields.Char('API Key')

    ############################################################################
    # Default Getters
    ############################################################################
    def get_default_api_key(self, cr, uid, ids, context=None):
        api_key = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'odoo_cenit.geneea_natural_language_processing_1_0.api_key', default=None, context=context
        )
        return {'api_key': api_key or ''}


    ############################################################################
    # Default Setters
    ############################################################################
    def set_api_key(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid, 'odoo_cenit.geneea_natural_language_processing_1_0.api_key', record.api_key or '',
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
