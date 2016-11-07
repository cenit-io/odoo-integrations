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
    'name': 'Import_io_1_0 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "## Introduction\n\nThe import.io API is a [REST](http://en.wikipedia.org/wiki/Representational_state_transfer)ful API. It is designed as much as possible to have resource-oriented URLs and to use HTTP status codes to indicate API status.\n\nWe use standard HTTP which can be understood by any HTTP client, and we support [CORS](http://enable-cors.org/) to allow you to interact with our API from a client-side web application. Remember, you should never expose your secret API key in any public client-side code.\n\nJSON is always returned from the API, including errors.\n\nimport.io uses conventional HTTP response codes to indicate success or failure of an API request. In general, codes in the 2xx range indicate success, codes in the 4xx range indicate an error that resulted from the provided information (e.g. a required parameter was missing), and codes in the 5xx range indicate an error with our servers.\n\nAll API requests *should* be made over HTTPS to `https://api.import.io/`\n\n\n\n## API Authentication\n\nYou authenticate to the import.io API by providing your API key as URL query string parameter `_apikey`. You can manage your API key from [your account](https://import.io/data/account/). In the My Settings page, the API in not URL encoded. To prevent a Base64 error, make sure to use a URI encode function for your query. You can also get an encoded API Key from the GET API or POST API tab in the application. Your API key allows unrestricted privileges your account, so keep it secret!\n\nWhen you are logged in, *submit your password in this page header* to see the API key in the API explorer below.\n\n## Quick Start\n\n### Basic concepts\n\n* import.io lets you publish dynamic APIs and Data Sets to its platform (object class `Connector`).\n  * To disambiguate between dynamic API created on the platform, and static APIs such as this, we use the term `Connector` within the import.io APIs to refer to a API or Data Set published to import.io.\n  * Extractors, Crawlers and Data Sets are just specializations of Connector.\n* You can create these via UI tooling, or by using the APIs detailed here.\n* The dynamic API definition for a Connector is versioned (object class `ConnectorVersion`); querying a connector by default queries the most recent version, whose id can be found on the `Connector` object (`latestVersionGuid`).\n* Each `ConnectorVersion` has a schema (object class `Schema`) defining its input and output properties.\n* All objects are accessible via the REST API.\n* The output properties are returned with the query data.\n  * Extra meta-data may be passed back depending on a output property [type](#data-types). \n  * All fields _may_ be multi-valued (i.e. arrays).\n\n### Convert a URL into data\n\nYou can use import.io magic to convert a URL into data tables over our API instantly.\n\n[Try it yourself!](?magic#!/Magic_Methods/magic)\n\n### Query a custom API\n\nCreate an API in the UI, do a query.\n\n[Try it yourself!](?query#!/Query_Methods/queryGet)\n\n## Data Types\n\nFor most output property types we also return `myvar/_source` with the original textual data. \n\n| Type  |  Returns |  Notes | \n| ---   |  ---     |  ---   |\n|   `STRING` | myvar  |  We normalize whitespace from text, and don't return empty strings | \n|  `CURRENCY` |  myvar, myvar/_currency, myvar/_source |  The ISO currency code is returned as `myvar/_currency`, the numeric value in `myvar` |  \n|  `INT` |  myvar, myvar/_source | 64 bit integer (`long`) | \n|  `DOUBLE` |  myvar, myvar/_source |  64 bit float | \n|  `LANG` |  myvar, myvar/_source |  3 letter ISO code | \n|  `COUNTRY` |  myvar, myvar/_source |  3 letter ISO code | \n|  `BOOLEAN` |  myvar, myvar/_source |  true if 1, yes, on, active, true, y | \n|  `URL` |  myvar, myvar/_text, myvar/_title, myvar/_source |  `myvar/_text` is the normalized text content of the anchor | \n|  `IMAGE` |  myvar,  myvar/_alt, myvar/_title, myvar/_source |   | \n|  `HTML` |  myvar | Raw HTML as well-formed XML  | \n|  `MAP` |  myvar |  JSON compatible map | ",
    'description': """
        Odoo - Import_io_1_0 integration via Cenit IO
    """,
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'view/config.xml',
        'view/wizard.xml'
    ],
    'installable': True
}
