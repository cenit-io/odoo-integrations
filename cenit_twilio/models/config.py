#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  config.py
#
#  Copyright 2015 D.H. Bahr <dhbahr@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import logging

from openerp import models, fields


_logger = logging.getLogger(__name__)


COLLECTION_NAME = "Twilio API Integration"
COLLECTION_VERSION = "1.0.0"


class CenitTwilioSettings(models.TransientModel):
    _name = "cenit.twilio.settings"
    _inherit = 'res.config.settings'

    account_sid = fields.Char('Account SID')
    auth_token = fields.Char('Auth Token')

    def get_default_account_sid(self, cr, uid, ids, context=None):
        account_sid = self.pool.get('ir.config_parameter').get_param(
            cr, uid,
            'odoo_cenit.twilio.account_sid', default = None,
            context = context
        )

        return {'account_sid': account_sid or ''}

    def get_default_auth_token(self, cr, uid, ids, context=None):
        auth_token = self.pool.get('ir.config_parameter').get_param(
            cr, uid,
            'odoo_cenit.twilio.auth_token', default = None,
            context = context
        )

        return {'auth_token': auth_token or ''}

    def set_account_sid(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get ("ir.config_parameter")
        for record in self.browse (cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid,
                "odoo_cenit.twilio.account_sid",
                record.account_sid or '',
                context = context
            )

    def set_auth_token(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get ("ir.config_parameter")
        for record in self.browse (cr, uid, ids, context=context):
            config_parameters.set_param (
                cr, uid,
                "odoo_cenit.twilio.auth_token",
                record.auth_token or '',
                context = context
            )

    def execute(self, cr, uid, ids, context=None):
        rc = super(CenitTwilioSettings, self).execute(
            cr, uid, ids, context=context
        )

        if not context.get('install', False):
            return rc

        objs = self.browse(cr, uid, ids)
        if not objs:
            return rc

        obj = objs[0]
        params = {
            '': obj.account_sid,
            '': obj.auth_token
        }
        installer = self.pool.get('cenit.collection.installer')
        installer.install_collection(
            cr, uid,
            'Twilio API Integration',
            params=params,
            context=None
        )

        return rc
