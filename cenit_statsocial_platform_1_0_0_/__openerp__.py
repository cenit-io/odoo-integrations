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
    'name': 'Statsocial_platform_1_0_0_ Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': 'API Reference: <br><br> The StatSocial API is organized around REST. Our API is designed to have predictable, resource-oriented URLs and to use HTTP response codes to indicate API errors. We use built-in HTTP features, like HTTP authentication and HTTP verbs, which can be understood by off-the-shelf HTTP clients, and we support cross-origin resource sharing to allow you to interact securely with our API from a client-side web application (remember that you should never expose your secret API key in any public website's client-side code). JSON will be returned in all responses from the API, including errors (though if you're using API bindings, we will convert the response to the appropriate language-specific object).<br><br>Contact help@statsocial.com to obtain a test API key',
    'description': """
        Odoo - Statsocial_platform_1_0_0_ integration via Cenit IO
    """,
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'view/config.xml',
        'view/wizard.xml'
    ],
    'installable': True
}
