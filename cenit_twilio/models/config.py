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

COLLECTION_NAME = "twilio_api_2010_04_01"
COLLECTION_VERSION = "1.0.0"
COLLECTION_PARAMS = {
    # WITHOUT COLLECTION_PARAMS.
}

class CenitIntegrationSettings(models.TransientModel):
    _name = "cenit.twilio_api_2010_04_01.settings"
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
    @api.model
    def install(self):
        installer = self.env['cenit.collection.installer']
        data = installer.get_collection_data(
            COLLECTION_NAME,
            version = COLLECTION_VERSION
        )

        installer.install_common_data(data['data'])
