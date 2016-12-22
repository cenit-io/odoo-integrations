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
    'name': 'Import_io_api_1_0 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "## Introduction\r\n\r\nThe import.io API is a [REST](http://en.wikipedia.org/wiki/Representational_state_transfer)ful API. It is designed as much as possible to have resource-oriented URLs and to use HTTP status codes to indicate API status.\r\n\r\nWe use standard HTTP which can be understood by any HTTP client. Remember, you should never expose your secret API key in any public client-side code.\r\n\r\nJSON is always returned from the API on success.\r\n\r\nimport.io uses conventional HTTP response codes to indicate success or failure of an API request. In general, codes in the 2xx range indicate success, codes in the 4xx range indicate an error that resulted from the provided information (e.g. a required parameter was missing), and codes in the 5xx range indicate an error with our servers.\r\n\r\nAll API requests *should* be made over HTTPS to `https://api.import.io/`\r\n\r\n(You can find our legacy docs [here](/legacy).)\r\n\r\n\r\n\r\n## API Authentication\r\n\r\nYou authenticate to the import.io API by providing your API key as URL query string parameter `_apikey`. You can manage your API key from [your account](https://import.io/data/account/).",
    'description': """
        Odoo - Import_io_api_1_0 integration via Cenit IO
    """,
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'view/config.xml',
        'view/wizard.xml'
    ],
    'installable': True
}
