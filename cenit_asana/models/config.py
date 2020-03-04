# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
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

from odoo import models, fields, api

_logger = logging.getLogger(__name__)

COLLECTION_NAME = "asana"
COLLECTION_VERSION = "1.0.0"
COLLECTION_PARAMS = {
    'Personal token': 'personal_token',
}


class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.asana.settings"
    _inherit = 'res.config.settings'

    ############################################################################
    # Pull Parameters
    ############################################################################
    personal_token = fields.Char('Personal token')

    ############################################################################
    # Default Getters
    ############################################################################
    @api.model
    def get_values(self):
        res = super(CenitIntegrationSettings, self).get_values()
        res.update(
            personal_token=self.env['ir.config_parameter'].sudo().get_param('odoo_cenit.asana.personal_token',
                                                                            default=None)
        )
        return res

    ############################################################################
    # Default Setters
    ############################################################################
    @api.multi
    def set_values(self):
        super(CenitIntegrationSettings, self).set_values()
        for record in self:
            self.env['ir.config_parameter'].sudo().set_param('odoo_cenit.asana.personal_token',
                                                             record.personal_token or '')

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
            version=COLLECTION_VERSION
        )

        params = {}
        for p in data.get('pull_parameters'):
            k = p['label']
            id_ = p.get('id')
            value = getattr(obj, COLLECTION_PARAMS.get(k))
            params.update({id_: value})

        installer.pull_shared_collection(data.get('id'), params=params)
        installer.install_common_data(data['data'])

        return rc
