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
    'name': 'Audiosear_ch_api_1_0_0 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "The Audiosear.ch API requires OAuth, which you can manage at <a href='/oauth/applications'>OAuth Applications</a>.<br/>API SDK clients available in <a href='https://github.com/popuparchive/audiosearch-client-python' target='_blank'>Python</a>, <a href='https://github.com/popuparchive/audiosearch-client-ruby' target='_blank'>Ruby</a>, <a href='https://github.com/popuparchive/audiosearch-client-php' target='_blank'>PHP</a>, <a href='https://github.com/popuparchive/audiosearch-client-node' target='_blank'>Node</a>, <a href='https://github.com/aljazeerair/AudiosearchClientJava' target='_blank'>Java</a>, and <a href='https://github.com/popuparchive/AudiosearchClientSwift' target='_blank'>Swift</a>.<br/>Read the <a href='https://github.com/popuparchive/audiosearch-cookbook/wiki'>API Cookbook</a> for easy copy-and-paste recipes.",
    'description': """
        Odoo - Audiosear_ch_api_1_0_0 integration via Cenit IO
    """,
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml'
    ],
    'installable': True
}
