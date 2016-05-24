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

        self.create_webhook(cr, uid, context)

        # rc2 = self.post_install(cr, uid, context=context)
        # if not rc2:
        #     raise exceptions.AccessError("Something went wrong")

    def create_webhook(self, cr, uid, context=None):
        hook_pool = self.pool.get("cenit.webhook")
        names_pool = self.pool.get("cenit.namespace")
        namesp_data = names_pool.search(cr, uid, [('name', '=', 'MyOdoo')], context=context)
        conn_pool = self.pool.get("cenit.connection")
        conn_data = conn_pool.search(cr, uid,
                                     [('name', '=', 'My Odoo host'), ('namespace', '=', namesp_data[0])], context=context)
        role_pool = self.pool.get("cenit.connection.role")

        if conn_data:
            hook_data = {
                "name": "Cenit webhook SUNAT",
                "path": "cenit/sunat/push",
                "namespace": namesp_data[0],
                "method": "post",
            }
            domain = [('name', '=', hook_data.get('name')), ('namespace', '=', hook_data.get('namespace'))]
            hook = hook_pool.search(cr, uid, domain, context= context)

            if not hook:
                hook = hook_pool.create(cr, uid, hook_data, context=context)
            #TODO Fix when hook exists
            # el1  hook[0].with_context(context= context).write({'namespace': hook_data.get('namespace')})
            #    # hook[0].write(cr, uid, {'namespace': hook_data.get('namespace')}, context= context)