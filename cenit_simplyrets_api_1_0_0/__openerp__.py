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
    'name': 'Simplyrets_api_1_0_0 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "The SimplyRETS API is an exciting step towards making it easier for\ndevelopers and real estate agents to build something awesome with...",
    'description': "The SimplyRETS API is an exciting step towards making it easier for\ndevelopers and real estate agents to build something awesome with\nreal estate data!\n\nThe documentation below makes live requests to our API using the\ntrial data. To get set up with the API using live MLS data, you\nmust have RETS credentials from your MLS, which you can then use to\ncreate an app with SimplyRETS. For more information on that\nprocess, please see our [FAQ](https://simplyrets.com/faq), [Getting\nStarted](https://simplyrets.com/blog/getting-set-up.html) page, or\n[contact us](https://simplyrets.com/\\#home-contact).\n\nBelow you'll find the API endpoints, query parameters, response bodies,\nand other information about using the SimplyRETS API. You can run\nqueries by clicking the 'Try it Out' button at the bottom of each\nsection.\n\n### Authentication\nThe SimplyRETS API uses Basic Authentication. When you create an\napp, you'll get a set of API credentials to access your\nlistings. If you're trying out the test data, you can use\n`simplyrets:simplyrets` for connecting to the API.\n\n### Media Types\nThe SimplyRETS API uses the `Accept` header to allow clients to\ncontrol media types (content versions). We maintain backwards\ncompatibility with API clients by allowing them to specify a\ncontent version. We highly recommend setting and explicity media\ntype when your application reaches production. Both the structure\nand content of our API response bodies is subject to change so we\ncan add new features while respecting the stability of applications\nwhich have already been developed.\n\nTo always use the latest SimplyRETS content version, simply use\n`application/json` in your application `Accept` header.\n\nIf you want to pin your clients media type to a specific version,\nyou can use the vendor-specific SimplyRETS media type, e.g.\n`application/vnd.simplyrets-v0.1+json\"`\n\nTo view all valid content-types for making an `OPTIONS`, make a\nrequest to the SimplyRETS api root\n\n`curl -XOPTIONS -u simplyrets:simplyrets https://api.simplyrets.com/`\n\nThe default media types used in our API responses may change in the\nfuture. If you're building an application and care about the\nstability of the API, be sure to request a specific media type in the\nAccept header as shown in the examples below.\n\nThe wordpress plugin automatically sets the `Accept` header for the\ncompatible SimplyRETS media types.\n\n### Pagination\nThere a few pieces of useful information about each request stored\nin the HTTP Headers:\n\n- `X-Total-Count` shows you the total amount of listings that match\n  your current query.\n- `Link` contains pre-built pagination links for accessing the next\n'page' of listings that match your query. Read more about that\n[here](https://simplyrets.com/blog/api-pagination.html).\n",
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml'
    ],
    'installable': True
}
