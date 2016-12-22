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

{
    'name': 'Ontraport_api_1_2_1 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "<p>Enter your App ID and API Key above. If you do not have an App ID or API Key login to your ONTRAPORT account and navigate <a href=\"https://app.ontraport.com/#!/api_settings/listAll\">here</a>. Authentication parameters must be sent in the request header as <strong>Api-Appid</strong> and <strong>Api-Key</strong>. Each ONTRAPORT account is allowed up to 180 requests per minute.</p>",
    'description': """
        Odoo - Ontraport_api_1_2_1 integration via Cenit IO
    """,
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml'
    ],
    'installable': True
}
