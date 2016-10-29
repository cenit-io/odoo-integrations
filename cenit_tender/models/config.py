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

COLLECTION_NAME = "tender"
COLLECTION_VERSION = "1.0.0"
COLLECTION_PARAMS = {
    "On connection 'Tender Connection' template parameter 'tender_api_key'":'tender_api_key',
    "On connection 'Tender Connection' template parameter 'tender_author_name'":'tender_author_name',
    "On connection 'Tender Connection' template parameter 'tender_author_email'":'tender_author_email',
    "On connection 'Tender Connection' template parameter 'tender_domain'":'tender_domain',
    "On connection 'Tender Connection' template parameter 'tender_category_id'":'tender_category_id',
    "On connection 'Tender Connection' template parameter 'tender_public'":'tender_public',
}

class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.tender.settings"
    _inherit = 'res.config.settings'

    ############################################################################
    # Pull Parameters
    ############################################################################
    tender_api_key = fields.Char('API Key')
    tender_author_name = fields.Char('Author Name')
    tender_author_email = fields.Char('Author Email')
    tender_domain = fields.Char('Domain')
    tender_category_id = fields.Char('Category')
    tender_public = fields.Char('Public')

    ############################################################################
    # Default Getters
    ############################################################################
    def get_default_tender_api_key(self, cr, uid, ids, context=None):
        tender_api_key = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'odoo_cenit.tender.tender_api_key', default=None, context=context
        )
        return {'tender_api_key': tender_api_key or ''}

    def get_default_tender_author_name(self, cr, uid, ids, context=None):
        tender_author_name = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'odoo_cenit.tender.tender_author_name', default=None, context=context
        )
        return {'tender_author_name': tender_author_name or ''}

    def get_default_tender_author_email(self, cr, uid, ids, context=None):
        tender_author_email = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'odoo_cenit.tender.tender_author_email', default=None, context=context
        )
        return {'tender_author_email': tender_author_email or ''}

    def get_default_tender_domain(self, cr, uid, ids, context=None):
        tender_domain = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'odoo_cenit.tender.tender_domain', default=None, context=context
        )
        return {'tender_domain': tender_domain or ''}

    def get_default_tender_category_id(self, cr, uid, ids, context=None):
        tender_category_id = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'odoo_cenit.tender.tender_category_id', default=None, context=context
        )
        return {'tender_category_id': tender_category_id or ''}

    def get_default_tender_public(self, cr, uid, ids, context=None):
        tender_public = self.pool.get('ir.config_parameter').get_param(
            cr, uid, 'odoo_cenit.tender.tender_public', default=None, context=context
        )
        return {'tender_public': tender_public or ''}


    ############################################################################
    # Default Setters
    ############################################################################
    def set_tender_api_key(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid, 'odoo_cenit.tender.tender_api_key', record.tender_api_key or '',
                context=context
            )

    def set_tender_author_name(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid, 'odoo_cenit.tender.tender_author_name', record.tender_author_name or '',
                context=context
            )

    def set_tender_author_email(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid, 'odoo_cenit.tender.tender_author_email', record.tender_author_email or '',
                context=context
            )

    def set_tender_domain(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid, 'odoo_cenit.tender.tender_domain', record.tender_domain or '',
                context=context
            )

    def set_tender_category_id(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid, 'odoo_cenit.tender.tender_category_id', record.tender_category_id or '',
                context=context
            )

    def set_tender_public(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid, 'odoo_cenit.tender.tender_public', record.tender_public or '',
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
