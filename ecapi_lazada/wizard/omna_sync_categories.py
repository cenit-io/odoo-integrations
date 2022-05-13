# -*- coding: utf-8 -*-

import requests
import base64
import json
import logging
import hmac
import hashlib
from datetime import datetime, timezone, time
from itertools import groupby
from odoo import models, api, exceptions, fields

_logger = logging.getLogger(__name__)


class OmnaSyncCategories(models.TransientModel):
    _name = 'omna.sync_categories_wizard'
    _inherit = 'omna.api'

    # sync_type = fields.Selection([('by_integration', 'By Integration'),
    #                               ('by_external_id', 'By External Id')], 'Import Type',
    #                              required=True, default='by_integration')
    integration_id = fields.Many2one('omna.integration', 'Integration')
    # category_id = fields.Many2one('product.category', 'Category')

    def sync_categories(self):
        try:
            limit = 100
            offset = 0
            requester = True
            categories = []

            # if self.sync_type == 'by_integration':
            while requester:
                response = self.get('integrations/%s/categories' % self.integration_id.integration_id, {'limit': limit, 'offset': offset, 'with_details': True})
                data = response.get('data')
                categories.extend(data)
                if len(data) < limit:
                    requester = False
                else:
                    offset += limit
            # else:
            #     external = self.category_id.omna_category_id
            #     if external:
            #         response = self.get(
            #             'integrations/%s/categories/%s' % (self.integration_id.integration_id, external),
            #             {})
            #     data = response.get('data')
            #     categories.append(data)

            category_obj = self.env['product.category']
            categories.sort(key=lambda x: x.get("name"))
            for category in categories:
                _logger.info(category)
                # self.category_lineal(category, self.integration_id.id)
                founded = self.env['product.category'].search(['&', '&', ('name', '=', category.get('name')), ('integration_id', '=', self.integration_id.id), ('omna_category_id', '=', category.get('id'))])
                if not founded:
                    category_obj.create({'name': category.get('name'), 'omna_category_id': category.get('id'),
                                         'integration_id': self.integration_id.id})
                else:
                    founded.write({'name': category.get('name'), 'omna_category_id': category.get('id'),
                             'integration_id': self.integration_id.id})

            self.env.cr.commit()

            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)

    # # def category_tree(self, arr, parent_id, category_id, integration_id, category_obj):
    # def category_tree(self, arr, parent_id, category_id, integration_id, category_obj):
    #     if len(arr) == 1:
    #         name = arr[0]
    #         # c = category_obj.search(['|', ('omna_category_id', '=', category_id), '&',
    #         #                          ('name', '=', name), ('parent_id', '=', parent_id), ('integration_id', '=', integration_id)], limit=1)
    #         c = category_obj.search(['&', ('omna_category_id', '=', category_id), '&', '&', ('name', '=', name), ('parent_id', '=', parent_id), ('integration_id', '=', integration_id)], limit=1)
    #         if not c:
    #             category_obj.create({'name': name, 'omna_category_id': category_id, 'parent_id': parent_id, 'integration_id': integration_id})
    #         else:
    #             c.write({'name': name, 'parent_id': parent_id, 'integration_id': integration_id})
    #
    #         return
    #     elif len(arr) > 1:
    #         name = arr[0]
    #         c = category_obj.search([('name', '=', name), ('integration_id', '=', integration_id)], limit=1)
    #         if not c:
    #             c= category_obj.create({'name': name, 'parent_id': parent_id, 'integration_id': integration_id})
    #
    #         self.category_tree(arr[1:], c.id if c else False, category_id, integration_id, category_obj)
