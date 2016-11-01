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
    'name': 'Hhs_media_services_2 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "\n<div class=\"swagger-ui-wrap extraFooter\"><h3>Common Features / Behaviors</h3>\n    <div class=\"features\">\n        <ul>\n            <li><strong>* \"sort\" param:</strong> supports multi column sorting through the use of commas as delimiters, and a hyphen to denote descending order.\n                <br/>\n                <strong><span>Examples:</span></strong>\n                <ul>\n                    <li><span class=\"example\">name</span><span class=\"description\">sort results by name ascending</span></li>\n                    <li><span class=\"example\">-name</span><span class=\"description\">sort results by name descending</span></li>\n                    <li><span class=\"example\">-name,id</span><span class=\"description\">sort results by name descending and then by id ascending</span></li>\n                    <li><span class=\"example\">id,-dateContentAuthored</span><span class=\"description\">sort results by id ascending and then date descending</span></li>\n                </ul>\n            </li>\n            <li><strong>Date formats:</strong> Date input format is expected to be based on <a href=\"http://www.ietf.org/rfc/rfc3339.txt\">RFC 3339</a>. <br/>\n                <span><strong>Example:</strong></span>\n                <ul><li>2013-11-18T18:43:01Z</li></ul>\n            </li>\n        </ul>\n    </div>\n</div>\n",
    'description': """
        Odoo - Hhs_media_services_2 integration via Cenit IO
    """,
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml'
    ],
    'installable': True
}
