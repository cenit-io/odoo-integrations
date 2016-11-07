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
    'name': 'Core_api_v2_2_0 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "<p style=\"text-align: justify;\">This is a documentation for CORE API v2.0. You can use the API to access the \r\n    resources harvested and enriched by CORE. If you encounter any problems with the API, please report them to us.</p>\r\n\r\n<h2>Overview</h2>\r\n<p style=\"text-align: justify;\">The API is organised by resource type. The resources are <b>articles</b>, \r\n    <b>journals</b> and <b>repositories</b> and are represented using JSON data format. Furthermore, \r\n    each resource has a list of methods. The API also provides two global methods for accessing all resources at once.</p>\r\n\r\n<h2>Response format</h2>\r\n<p style=\"text-align: justify;\">Response for each query contains two fields: <b>status</b> and <b>data</b>.\r\n    In case of an error status, the data field is empty. The data field contains a single object\r\n    in case the request is for a specific identifier (e.g. CORE ID, CORE repository ID, etc.), or  \r\n    contains a list of objects, for example for search queries. In case of batch requests, the response\r\n    is an array of objects, each of which contains its own <b>status</b> and <b>data</b> fields.\r\n    For search queries the response contains an additional field <b>totalHits</b>, which is the \r\n    total number of items which match the search criteria.</p>\r\n\r\n<h2>Search query syntax</h2>\r\n\r\n<p style=\"text-align: justify\">All of the API search methods allow using complex search queries.\r\n    The query can be a simple string or it can be built using terms and operators described in Elasticsearch\r\n    <a href=\"http://www.elastic.co/guide/en/elasticsearch/reference/1.4/query-dsl-query-string-query.html#query-string-syntax\">documentation</a>.\r\n    The usable field names are <strong>title</strong>, <strong>description</strong>, <strong>fullText</strong>, \r\n    <strong>authorsString</strong>, <strong>publisher</strong>, <strong>repositories.id</strong>, <strong>repositories.name</strong>, \r\n    <strong>doi</strong>, <strong>oai</strong>, <strong>identifiers</strong> (which is a list of article identifiers including OAI, URL, etc.), <strong>language.name</strong> \r\n    and <strong>year</strong>. Some example queries:\r\n</p>\r\n\r\n<ul style=\"margin-left: 30px;\">\r\n    <li><p>title:psychology and language.name:English</p></li>\r\n    <li><p>repositories.id:86 AND year:2014</p></li>\r\n    <li><p>identifiers:\"oai:aura.abdn.ac.uk:2164/3837\" OR identifiers:\"oai:aura.abdn.ac.uk:2164/3843\"</p></li>\r\n    <li><p>doi:\"10.1186/1471-2458-6-309\"</p></li>\r\n</ul>\r\n\r\n<h2>Sort order</h2>\r\n\r\n<p style=\"text-align: justify;\">For search queries, the results are ordered by relevance score. For batch \r\n    requests, the results are retrieved in the order of the requests.</p>\r\n\r\n<h2>Parameters</h2>\r\n<p style=\"text-align: justify;\">The API methods allow different parameters to be passed. Additionally, there is an API key parameter which is common to all API methods. For all API methods \r\n    the API key can be provided either as a query parameter or in the request header. If the API key \r\n    is not provided, the API will return HTTP 401 error. You can register for an API key <a href=\"/services#api\">here</a>.</p>\r\n\r\n<h2>API methods</h2>",
    'description': """
        Odoo - Core_api_v2_2_0 integration via Cenit IO
    """,
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'view/config.xml',
        'view/wizard.xml'
    ],
    'installable': True
}
