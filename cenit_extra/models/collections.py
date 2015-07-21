#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  collections.py
#
#  Copyright 2015 D.H. Bahr <dhbahr@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import logging
import simplejson

from openerp import models, fields, api


_logger = logging.getLogger(__name__)


class CenitCollection(models.Model):

    @api.model
    def _update_collection_list(self):
        param_pool = self.env['cenit.collection.parameter']

        path = "/setup/shared_collection"
        cenit_api = self.env['cenit.api']
        rc = cenit_api.get(path)

        collections = []
        for entry in rc:
            collection = entry.get('shared_collection')
            data = {
                'sharedID': collection.get('id'),
                'name': collection.get('name'),
                'description': collection.get('description'),
            }

            domain = [('sharedID','=',data.get('sharedID'))]
            candidates = self.search(domain)

            if not candidates:
                coll = self.create(data)
            else:
                coll = candidates[0]
                coll.write(data)

            params = collection.get('pull_parameters', [])
            param_list = []
            strict_keys = []

            for param in params:
                param_data = {
                    'cenitID': param.get('id'),
                    'name': param.get('label')
                }
                domain = [('cenitID', '=', param_data.get('cenitID'))]
                candidates = param_pool.search(domain)

                if not candidates:
                    param_list.append([0, False, param_data])
                else:
                    p = candidates[0]
                    param_list.append([1, p.id, param_data])

                strict_keys.append(param_data.get('name'))

            domain = [
                ('name', 'not in', strict_keys),
                ('collection', '=', coll.id)
            ]
            candidates = param_pool.search(domain)
            for candidate in candidates:
                param_list.append([2, candidate.id, False])

            rc = coll.write({'parameters': param_list})

        xml_id = 'oe_cenit_client.view_cenit_collection_tree'
        args = (self.env.cr, self.env.uid, xml_id)
        view_id = self.pool.get('ir.model.data').xmlid_to_res_id(*args)
        return {
            "type": "ir.actions.act_window",
            "view_id": view_id,
            "res_model": "cenit.collection",
            "view_type": "form",
            "view_mode": "tree",
        }

    @api.one
    def install_collection(self):
        installer = self.env['cenit.collection.installer']

        params = dict(
            (param.cenitID, param.value) for param in self.parameters
        )
        rc = installer.install_collection(self.sharedID, params=params)

        return rc

    _name = "cenit.collection"

    cenitID = fields.Char('CenitID')
    sharedID = fields.Char('SharedID')
    name = fields.Char('Name')
    description = fields.Text('Description')
    #~ image = fields.Binary('Image')

    parameters = fields.One2many(
        'cenit.collection.parameter',
        'collection',
        string = 'Pull Parameters'
    )


class CenitCollectionPullParameter(models.Model):
    _name = "cenit.collection.parameter"

    cenitID = fields.Char('CenitID')
    name = fields.Char('Name')
    value = fields.Char('Value')

    collection = fields.Many2one(
        'cenit.collection',
        string="Collection",
        ondelete="cascade",
        required=True
    )
