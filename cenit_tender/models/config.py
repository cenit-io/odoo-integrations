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

COLLECTION_NAME = "tender"
COLLECTION_VERSION = "1.0.0"
COLLECTION_PARAMS = {
    'API Key':'tender_api_key',
    'Author Name':'tender_author_name',
    'Author Email':'tender_author_email',
    'Domain':'tender_domain',
    'Category':'tender_category_id',
    'Public':'tender_public',
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
    def get_default_tender_api_key(self, context):
        tender_api_key = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.tender.tender_api_key', default=None
        )
        return {'tender_api_key': tender_api_key or ''}

    def get_default_tender_author_name(self, context):
        tender_author_name = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.tender.tender_author_name', default=None
        )
        return {'tender_author_name': tender_author_name or ''}

    def get_default_tender_author_email(self, context):
        tender_author_email = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.tender.tender_author_email', default=None
        )
        return {'tender_author_email': tender_author_email or ''}

    def get_default_tender_domain(self, context):
        tender_domain = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.tender.tender_domain', default=None
        )
        return {'tender_domain': tender_domain or ''}

    def get_default_tender_category_id(self, context):
        tender_category_id = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.tender.tender_category_id', default=None
        )
        return {'tender_category_id': tender_category_id or ''}

    def get_default_tender_public(self, context):
        tender_public = self.env['ir.config_parameter'].get_param(
            'odoo_cenit.tender.tender_public', default=None
        )
        return {'tender_public': tender_public or ''}


    ############################################################################
    # Default Setters
    ############################################################################
    def set_tender_api_key(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.tender.tender_api_key', record.tender_api_key or ''
            )

    def set_tender_author_name(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.tender.tender_author_name', record.tender_author_name or ''
            )

    def set_tender_author_email(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.tender.tender_author_email', record.tender_author_email or ''
            )

    def set_tender_domain(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.tender.tender_domain', record.tender_domain or ''
            )

    def set_tender_category_id(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.tender.tender_category_id', record.tender_category_id or ''
            )

    def set_tender_public(self):
        config_parameters = self.env['ir.config_parameter']
        for record in self.browse(self.ids):
            config_parameters.set_param (
                'odoo_cenit.tender.tender_public', record.tender_public or ''
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
