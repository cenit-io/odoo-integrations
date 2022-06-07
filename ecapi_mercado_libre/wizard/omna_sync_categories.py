# -*- coding: utf-8 -*-

import requests
import base64
import json
import logging
import hmac
import hashlib
import threading
import time
# from datetime import datetime, timezone, time
from itertools import groupby
from odoo import models, api, exceptions, fields

_logger = logging.getLogger(__name__)

maxthreads = 10
sema = threading.Semaphore(value=maxthreads)
threads = list()


class OmnaSyncCategories(models.TransientModel):
    _name = 'omna.sync_categories_wizard'
    _inherit = 'omna.api'

    # sync_type = fields.Selection([('by_integration', 'By Integration'),
    #                               ('by_external_id', 'By External Id')], 'Import Type',
    #                              required=True, default='by_integration')
    integration_id = fields.Many2one('omna.integration', 'Integration', domain=lambda self:[('company_id', '=', self.env.company.id)])
    # category_id = fields.Many2one('product.category', 'Category')



    def function_aux(self, limit, offset, integration_id, categories):
        sema.acquire()
        _logger.info("Starting process %s" % (offset,))
        with api.Environment.manage():
            # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            response = self.get('integrations/%s/categories' % integration_id,
                                {'limit': limit, 'offset': offset, 'with_details': True})
            data = response.get('data')
            categories.extend(data)
            new_cr.close()
        sema.release()




    def sync_categories(self):
        try:
            limit = 100
            offset = 0
            categories = []
            response_temp = self.get('integrations/%s/categories' % self.integration_id.integration_id, {'limit': 5, 'offset': 0, 'with_details': True})
            total_categories = response_temp.get('pagination').get('total')

            for item in list(range(0, total_categories, limit)):
                threaded_api_request = threading.Thread(target=self.function_aux, args=([limit, item, self.integration_id.integration_id, categories]))
                threaded_api_request.start()
                threads.append(threaded_api_request)

            for item in threads:
                item.join()
            # while requester:
            #     response = self.get('integrations/%s/categories' % self.integration_id.integration_id, {'limit': limit, 'offset': offset, 'with_details': True})
            #     data = response.get('data')
            #     categories.extend(data)
            #     if len(data) < limit:
            #         requester = False
            #     else:
            #         offset += limit

            # time.sleep(300)
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
