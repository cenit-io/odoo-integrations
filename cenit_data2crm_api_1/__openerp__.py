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
    'name': 'Data2crm_api_1 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "<p>Make use of our in-depth documentation to get more information about the various functions of the service. Those willing to explore the mechanics of Data2CRM.API can test it in live regime using the short code samples.</p><p>Select CRM: <span id=\"docs-select-crm\" style=\"font-weight: bold\">Loading... please wait</span></p><p>Here are the API access keys:<br><b>X-API2CRM-USERKEY</b>: <span id=\"docs-user-key\">e2a6379ab878ae7e58119d4ec842bf9c926e05b5</span><br><b>X-API2CRM-CRMKEY</b>: <span id=\"docs-crm-key\">7ae5b17008fb414d84981191cf3b66a476ef8bef</span></p><p id=\"docs-crm-access\">The CRM access details are:<br><b>URL</b>: <a id=\"docs-crm-url\" href=\"https://login.salesforce.com/\" target=\"_blank\">https://login.salesforce.com/</a><br><b>E-mail / Username</b>: <span id=\"docs-crm-username\">developers.data2crm.api+1@magneticone.com</span><br><b>Password</b>: <span id=\"docs-crm-password\">data2crmapi123</span></p>",
    'description': """
        Odoo - Data2crm_api_1 integration via Cenit IO
    """,
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml'
    ],
    'installable': True
}
