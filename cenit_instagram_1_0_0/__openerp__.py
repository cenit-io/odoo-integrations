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
    'name': 'Instagram_1_0_0 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "Description of Instagram RESTful API.\n\nCurrent limitations:\n  * Instagram service does not support [cross origin headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Access_control_CORS)\n  for security reasons, therefore it is not possible to use Swagger UI and make API calls directly from browser.\n  * Modification API requests (`POST`, `DELETE`) require additional security [scopes](https://instagram.com/developer/authorization/)\n  that are available for Apps [created on or after Nov 17, 2015](http://instagram.com/developer/review/) and\n  started in [Sandbox Mode](http://instagram.com/developer/sandbox/).\n  * Consider the [Instagram limitations](https://instagram.com/developer/limits/) for API calls that depends on App Mode.\n\n**Warning:** For Apps [created on or after Nov 17, 2015](http://instagram.com/developer/changelog/) API responses\ncontaining media objects no longer return the `data` field in `comments` and `likes` nodes.\n\nLast update: 2015-11-28\n",
    'description': """
        Odoo - Instagram_1_0_0 integration via Cenit IO
    """,
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'view/config.xml',
        'view/wizard.xml'
    ],
    'installable': True
}
