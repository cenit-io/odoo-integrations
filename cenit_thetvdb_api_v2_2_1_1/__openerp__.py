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
    'name': 'Thetvdb_api_v2_2_1_1 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "...",
    'description': "API v2 targets v1 functionality with a few minor additions. The API is accessible via https://api.thetvdb.com and provides the following REST endpoints in JSON format.\n\n\nHow to use this API documentation\n----------------\n\n\nYou may browse the API routes without authentication, but if you wish to send requests to the API and see response data, then you must authenticate.\n1. Obtain a JWT token by `POST`ing  to the `/login` route in the `Authentication` section with your API key and credentials.\n1. Paste the JWT token from the response into the \"JWT Token\" field at the top of the page and click the 'Add Token' button.\n\n\nYou will now be able to use the remaining routes to send requests to the API and get a response.\n\n\nLanguage Selection\n----------------\n\n\nLanguage selection is done via the `Accept-Language` header. At the moment, you may only pass one language abbreviation in the header at a time. Valid language abbreviations can be found at the `/languages` route..\n\n\nAuthentication\n----------------\n\n\nAuthentication to use the API is similar to the How-to section above. Users must `POST` to the `/login` route with their API key and credentials in the following format in order to obtain a JWT token.\n\n`{\"apikey\":\"APIKEY\",\"username\":\"USERNAME\",\"userkey\":\"USERKEY\"}`\n\nNote that the username and key are ONLY required for the `/user` routes. The user's key is labled `Account Identifier` in the account section of the main site.\nThe token is then used in all subsequent requests by providing it in the `Authorization` header. The header will look like: `Authorization: Bearer <yourJWTtoken>`. Currently, the token expires after 24 hours. You can `GET` the `/refresh_token` route to extend that expiration date.\n\n\nVersioning\n----------------\n\n\nYou may request a different version of the API by including an `Accept` header in your request with the following format: `Accept:application/vnd.thetvdb.v$VERSION`. This documentation automatically uses the version seen at the top and bottom of the page.",
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'view/config.xml',
        'view/wizard.xml'
    ],
    'images': ['static/images/banner.jpg'],
    'installable': True
}
