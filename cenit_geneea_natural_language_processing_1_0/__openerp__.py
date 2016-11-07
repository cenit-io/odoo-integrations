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
    'name': 'Geneea_natural_language_processing_1_0 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "<div class=\"api-description\">\r\n    <h2>Authentication</h2>\r\n    <p>For all calls, supply your API key. <a href=\"https://geneea.3scale.net/\">Sign up to <em>obtain the key</em></a>.</p>\r\n    <p>\r\n        Our API supports both <em>unencrypted (HTTP)</em> and <em>encrypted (HTTPS)</em> protocols.\r\n        However, for security reasons, we strongly encourage using only the encrypted version.\r\n    </p>\r\n    <p>The API key should be supplied as either a request parameter <code>user_key</code> or in <code>Authorization</code> header.</p>\r\n    <pre><code>Authorization: user_key &lt;YOUR_API_KEY&gt;</code></pre>\r\n\r\n    <h2>API operations</h2>\r\n    <p>\r\n        All API operations can perform analysis on supplied raw text or on text extracted from a given URL.\r\n        Optionally, one can supply additional information which can make the result more precise. An example\r\n        of such information would be the language of text or a particular text extractor for URL resources.\r\n    </p>\r\n    <p>The supported types of analyses are:</p>\r\n    <ul>\r\n        <li><strong>lemmatization</strong> &longrightarrow;\r\n            Finds out lemmata (basic forms) of all the words in the document.\r\n        </li>\r\n        <li><strong>correction</strong> &longrightarrow;\r\n            Performs correction (diacritization) on all the words in the document.\r\n        </li>\r\n        <li><strong>topic detection</strong> &longrightarrow;\r\n            Determines a topic of the document, e.g. finance or sports.\r\n        </li>\r\n        <li><strong>sentiment analysis</strong> &longrightarrow;\r\n            Determines a sentiment of the document, i.e. how positive or negative the document is.\r\n        </li>\r\n        <li><strong>named entity recognition</strong> &longrightarrow;\r\n            Finds named entities (like person, location, date etc.) mentioned the the document.\r\n        </li>\r\n    </ul>\r\n\r\n    <h2>Encoding</h2>\r\n    <p>The supplied text is expected to be in UTF-8 encoding, this is especially important for non-english texts.</p>\r\n\r\n    <h2>Returned values</h2>\r\n    <p>The API calls always return objects in serialized JSON format in UTF-8 encoding.</p>\r\n    <p>\r\n        If any error occurs, the HTTP response code will be in the range <code>4xx</code> (client-side error) or\r\n        <code>5xx</code> (server-side error). In this situation, the body of the response will contain information\r\n        about the error in JSON format, with <code>exception</code> and <code>message</code> values.\r\n    </p>\r\n\r\n    <h2>URL limitations</h2>\r\n    <p>\r\n        All the requests are semantically <code>GET</code>. However, for longer texts, you may run into issues\r\n        with URL length limit. Therefore, it's possible to always issue a <code>POST</code> request with all\r\n        the parameters encoded as a JSON in the request body.\r\n    </p>\r\n    <p>Example:</p>\r\n    <pre><code>\r\n        POST /s1/sentiment\r\n        Content-Type: application/json\r\n\r\n        {\"text\":\"There is no harm in being sometimes wrong - especially if one is promptly found out.\"}\r\n    </code></pre>\r\n    <p>This is equivalent to <code>GET /s1/sentiment?text=There%20is%20no%20harm...</code></p>\r\n\r\n    <h2>Request limitations</h2>\r\n    <p>\r\n        The API has other limitations concerning the size of the HTTP requests. The maximal allowed size of any\r\n        POST request body is <em>512 KiB</em>. For request with a URL resource, the maximal allowed number of\r\n        extracted characters from each such resource is <em>100,000</em>.\r\n    </p>\r\n\r\n    <h2>More information</h2>\r\n    <p>\r\n        <a href=\"https://geneea.atlassian.net/wiki/display/IPD/The+Interpretor+API+Public+Documentation\" target=\"_blank\">\r\n        The Interpretor Public Documentation\r\n        </a>\r\n    </p>\r\n</div>\r\n",
    'description': """
        Odoo - Geneea_natural_language_processing_1_0 integration via Cenit IO
    """,
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'view/config.xml',
        'view/wizard.xml'
    ],
    'installable': True
}
