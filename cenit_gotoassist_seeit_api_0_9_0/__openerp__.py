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
    'name': 'Gotoassist_seeit_api_0_9_0 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "<p>Allows you to integrate GoToAssist Seeit into your own solutions.</p><p>General notes:<ul><li>GoToAssist Seeit sessions are identified by their uuid. The more readable 9 digit support key (e.g. 123-456-789) may be reused later for another session and thus cannot be used to unambiguously identify a session.</li><li>If not explicitly stated otherwise all timestamps represent the number of milliseconds since 1970-01-01 in UTC (similar to a Unix Timestamp but with millisecond resolution)</li></ul></p>",
    'description': """
        Odoo - Gotoassist_seeit_api_0_9_0 integration via Cenit IO
    """,
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml'
    ],
    'installable': True
}
