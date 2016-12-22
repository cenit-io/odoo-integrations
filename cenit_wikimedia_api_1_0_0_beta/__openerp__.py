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
    'name': 'Wikimedia_api_1_0_0_beta Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "This API aims to provide coherent and low-latency access to Wikimedia content and services. It is currently in beta testing, so things aren't completely locked down yet. Each entry point has explicit stability markers to inform you about development status and change policy, according to [our API version policy](https://www.mediawiki.org/wiki/API_versioning).\r\n### High-volume access\r\n  - Don't perform more than 200 requests/s to this API.\r\n  - Set a unique `User-Agent` header that allows us to contact you\r\n    quickly. Email addresses or URLs of contact pages work well.\r\n",
    'description': """
        Odoo - Wikimedia_api_1_0_0_beta integration via Cenit IO
    """,
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'view/config.xml',
        'view/wizard.xml'
    ],
    'installable': True
}
