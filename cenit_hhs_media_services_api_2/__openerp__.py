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
    'name': 'Hhs_media_services_api_2 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "<div class=\"swagger-ui-wrap extraFooter\"><h3>Common Features / Behaviors</h3>\n    <div class=\"features\">\n        <ul>...",
    'description': "\r\n<div class=\"swagger-ui-wrap extraFooter\"><h3>Common Features / Behaviors</h3>\r\n    <div class=\"features\">\r\n        <ul>\r\n            <li><strong>* \"sort\" param:</strong> supports multi column sorting through the use of commas as delimiters, and a hyphen to denote descending order.\r\n                <br/>\r\n                <strong><span>Examples:</span></strong>\r\n                <ul>\r\n                    <li><span class=\"example\">name</span><span class=\"description\">sort results by name ascending</span></li>\r\n                    <li><span class=\"example\">-name</span><span class=\"description\">sort results by name descending</span></li>\r\n                    <li><span class=\"example\">-name,id</span><span class=\"description\">sort results by name descending and then by id ascending</span></li>\r\n                    <li><span class=\"example\">id,-dateContentAuthored</span><span class=\"description\">sort results by id ascending and then date descending</span></li>\r\n                </ul>\r\n            </li>\r\n            <li><strong>Date formats:</strong> Date input format is expected to be based on <a href=\"http://www.ietf.org/rfc/rfc3339.txt\">RFC 3339</a>. <br/>\r\n                <span><strong>Example:</strong></span>\r\n                <ul><li>2013-11-18T18:43:01Z</li></ul>\r\n            </li>\r\n        </ul>\r\n    </div>\r\n</div>\r\n",
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml'
    ],
    'images': ['static/images/banner.jpg'],
    'installable': True
}
