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
    'name': 'Queen_api_2_9_18 Integration',
    'version': '0.1',
    'author': 'Cenit IO',
    'website': 'https://cenit.io',
    # ~ 'license': 'LGPL-3',
    'category': 'Extra Tools',
    'summary': "...",
    'description': "<p>This is the API for building Mondia-Media-Products, like Tops.</p><p>Every call need a valid client or user-token.</p><p><ol><li>Client-Token can be get at our Police-API</li><li>User-Token can be get through a login on a customer specific Life-Cycle-Service</li><li>UseCases regarding Login, Register, Subscribe (incl. Payment) will be done by the Life-Cycle-Service</li></ol></p>",
    'depends': ['cenit_base'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml'
    ],
    'images': ['static/images/banner.jpg'],
    'installable': True
}
