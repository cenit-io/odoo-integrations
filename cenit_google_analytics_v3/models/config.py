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

COLLECTION_NAME = "google_analytics_v3"
COLLECTION_VERSION = "0.1"
COLLECTION_PARAMS = {
    # WITHOUT COLLECTION_PARAMS.
}

class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.google_analytics_v3.settings"
    _inherit = 'res.config.settings'

    ############################################################################
    # Pull Parameters
    ############################################################################
    # WITHOUT PULL PARAMETERS.

    ############################################################################
    # Default Getters
    ############################################################################
    # WITHOUT GETTERS.

    ############################################################################
    # Default Setters
    ############################################################################
    # WITHOUT SETTERS.

    ############################################################################
    # Actions
    ############################################################################
    def install(self, cr, uid, context=None):
        installer = self.pool.get('cenit.collection.installer')
        data = installer.get_collection_data(
            cr, uid,
            COLLECTION_NAME,
            version = COLLECTION_VERSION,
            context = context
        )

        installer.install_collection(cr, uid, {'name': COLLECTION_NAME})
