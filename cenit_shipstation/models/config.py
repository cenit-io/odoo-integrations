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

COLLECTION_NAME = "shipstation"
COLLECTION_VERSION = "1.0.0"
COLLECTION_PARAMS = {}


class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.shipstation.settings"
    _inherit = 'res.config.settings'

    ############################################################################
    # Pull Parameters
    ############################################################################
    key = fields.Char('Shipstation Key')
    secret = fields.Char('Shipstation Secret')
    store_id = fields.Char('Shipstation Store')

    ############################################################################
    # Default Getters
    ############################################################################
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

    def get_default_store_id(self, cr, uid, ids, context=None):
        store_id = self.pool.get('ir.config_parameter').get_param(
            cr, uid,
            'odoo_cenit.shipstation.store_id', default=None,
            context=context
        )
        return {'store_id': store_id or ''}
    
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

    def set_store_id(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get('ir.config_parameter')
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(
                cr, uid,
                'odoo_cenit.shipstation.store_id', record.store_id or '',
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
            version=COLLECTION_VERSION,
            context=context
        )

        params = {}
        for p in data.get('params'):
            k = p.get('key')
            id_ = p.get('id')
            value = getattr(obj, COLLECTION_PARAMS.get(k, k))
            params.update({id_: value})

        installer.install_collection(
            cr, uid,
            data.get('id'),
            params=params,
            context=context
        )

        # rc2 = self.post_install(cr, uid, context=context)
        # if not rc2:
        #     raise exceptions.AccessError("Something went wrong")
        return rc

    # def post_install(self, cr, uid, context=None):
    #     icp = self.pool.get("ir.config_parameter")
    #
    #     hook_pool = self.pool.get("cenit.webhook")
    #     role_pool = self.pool.get("cenit.connection.role")
    #     flow_pool = self.pool.get("cenit.flow")
    #     evnt_pool = self.pool.get("cenit.event")
    #     trns_pool = self.pool.get("cenit.translator")
    #     schm_pool = self.pool.get("cenit.schema")
    #     lbry_pool = self.pool.get("cenit.library")
    #
    #     cenit_api = self.pool.get("cenit.api")
    #     cenit_installer = self.pool.get("cenit.collection.installer")
    #
    #     hook_id = icp.get_param(cr, uid, "cenit.odoo_feedback.hook", default=1)
    #     role_id = icp.get_param(cr, uid, "cenit.odoo_feedback.role", default=1)
    #
    #     SELF_NSPACE = "Odoo"
    #     LIB_NAME = "Shipstation"
    #     domain = [("name", "=", LIB_NAME)]
    #     lbry = lbry_pool.search(cr, uid, domain, context=context)
    #     if not lbry:
    #         err_msg = "Expected Cenit Library '%s' not found" % (LIB_NAME,)
    #         _logger.error(err_msg)
    #         raise exceptions.MissingError(err_msg)
    #     lib_id = lbry and lbry[0]
    #
    #     SCH_NAME = "Order.json"
    #     domain = [("name", "=", SCH_NAME), ("library", "=", lib_id)]
    #     schm = schm_pool.search(cr, uid, domain, context=context)
    #     if not schm:
    #         err_msg = "Expected Cenit Schema '[%s] %s' not found" % (
    #             LIB_NAME, SCH_NAME)
    #         _logger.error(err_msg)
    #         raise exceptions.MissingError(err_msg)
    #     sch_id = schm and schm[0]
    #     schema = schm_pool.browse(cr, uid, sch_id)
    #
    #     TR_NAME = "Export Model"
    #     NSPACE = "shipstation"
    #     domain = [("name", "=", TR_NAME), ("namespace", "=", LIB_NAME)]
    #     trns = trns_pool.search(cr, uid, domain, context=context)
    #     if not trns:
    #         err_msg = "Expected Cenit Translator '[%s] %s' not found" % (
    #             LIB_NAME, TR_NAME)
    #         _logger.error(err_msg)
    #         raise exceptions.MissingError(err_msg)
    #     trans_id = trns and trns[0]
    #
    #     EV_NAME = "Shipstation Order update_at"
    #     evnt_data = {"event": {
    #         "namespace": SELF_NSPACE,
    #         "name": EV_NAME,
    #         "_type": "Setup::Observer",
    #         "data_type": {
    #             "_reference": True,
    #             "id": schema.cenitID
    #         },
    #         "triggers":
    #             '{"updated_at":{"0":{"o":"_presence_change","v":["","",""]}}}',
    #         "_primary": ["namespace", "name"]
    #     }}
    #     rc = cenit_api.post(cr, uid, "/setup/push", evnt_data)
    #     rc_data = rc.get('success', {}).get("events", [])
    #     if rc_data:
    #         cenit_installer._install_events(cr, uid, rc_data)
    #
    #     domain = [("name", "=", EV_NAME), ("namespace", "=", "Odoo")]
    #     evnt = evnt_pool.search(cr, uid, domain, context=context)
    #     if not evnt:
    #         err_msg = "Expected Cenit Event '%s' not found" % (EV_NAME,)
    #         _logger.error(err_msg)
    #         raise exceptions.MissingError(err_msg)
    #     ev_id = evnt and evnt[0]
    #
    #     FL_NAME = "{} API <- {} feedback".format(LIB_NAME, SCH_NAME)
    #
    #     flow_data = {
    #         "namespace": SELF_NSPACE,
    #         "name": FL_NAME,
    #         "format_": "application/json",
    #         "cenit_translator": trans_id,
    #         "connection_role": role_id,
    #         "webhook": hook_id,
    #         "schema": sch_id,
    #         "event": ev_id,
    #     }
    #
    #     domain = [
    #         ("namespace", "=", SELF_NSPACE),
    #         ("name", "=", FL_NAME),
    #     ]
    #     candidates = flow_pool.search(cr, uid, domain)
    #     fid = candidates and candidates[0]
    #     if fid:
    #         flow_pool.write(cr, uid, fid, flow_data)
    #     else:
    #         flow_pool.create(cr, uid, flow_data, context=context)
    #
    #     feedback_flows = ["Create Order",]
    #     for name in feedback_flows:
    #         domain = [("namespace", "=", NSPACE), ("name", "=", name)]
    #         rc = flow_pool.search(cr, uid, domain)
    #         fid = rc and rc[0]
    #
    #         if fid:
    #             flow = flow_pool.browse(cr, uid, fid)
    #             if flow.discard_events:
    #                 payload = {
    #                     "flow": {
    #                         "id": flow.cenitID,
    #                         "discard_events": False,
    #                     }
    #                 }
    #                 rc = cenit_api.post(cr, uid, "/setup/push", payload)
    #                 _logger.info("\n\nRC: %s\n", rc)
    #
    #     return True
