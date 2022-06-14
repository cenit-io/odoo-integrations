# -*- coding: utf-8 -*-

import requests
import base64
import json
import logging
import hmac
import hashlib
import threading
import time
from datetime import datetime, timezone, time
from odoo import models, api, exceptions, fields


_logger = logging.getLogger(__name__)

maxthreads = 10
sema = threading.Semaphore(value=maxthreads)
threads = list()


class OmnaSyncBrands(models.TransientModel):
    _name = 'omna.sync_brands_wizard'
    _inherit = 'omna.api'

    # sync_type = fields.Selection([('by_integration', 'By Integration'),
    #                               ('by_external_id', 'By External Id')], 'Import Type',
    #                              required=True, default='by_integration')
    integration_id = fields.Many2one('omna.integration', 'Integration', domain=lambda self:[('company_id', '=', self.env.company.id)])
    # brand_id = fields.Many2one('product.brand', 'Brand')
    # quantity_max = fields.Integer('Max Quantity', default=100)



    def function_aux(self, limit, offset, integration_id, brands):
        sema.acquire()
        _logger.info("Starting process %s" % (offset,))
        with api.Environment.manage():
            # As this function is in a new thread, I need to open a new cursor, because the old one may be closed
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            response = self.get('integrations/%s/brands' % integration_id, {'limit': limit, 'offset': offset, 'with_details': True})
            data = response.get('data')
            brands.extend(data)
            new_cr.close()
        sema.release()



    def sync_brands(self):
        try:
            limit = 100
            offset = 0
            brands = []
            response_temp = self.get('integrations/%s/brands' % self.integration_id.integration_id, {'limit': 5, 'offset': 0, 'with_details': True})
            total_brands = response_temp.get('pagination').get('total')

            for item in list(range(0, total_brands, limit)):
                threaded_api_request = threading.Thread(target=self.function_aux, args=([limit, item, self.integration_id.integration_id, brands]))
                threaded_api_request.start()
                threads.append(threaded_api_request)

            for item in threads:
                item.join()

            # if self.sync_type == 'by_integration':
            #     while requester:
            #         response = self.get('integrations/%s/brands' % self.integration_id.integration_id, {'limit': limit, 'offset': offset, 'with_details': 'true'})
            #         data = response.get('data')
            #         brands.extend(data)
            #         offset += limit
            #         if (len(data) < limit) or (offset == self.quantity_max):
            #             requester = False
            #
            # else:
            #     external = self.brand_id.omna_brand_id
            #     if external:
            #         response = self.get(
            #             'integrations/%s/brands/%s' % (self.integration_id.integration_id, external),
            #             {})
            #     data = response.get('data')
            #     brands.append(data)


            brand_obj = self.env['product.brand']
            for brand in brands:
                _logger.info(brand)
                act_brand = brand_obj.search([('omna_brand_id', '=', brand.get('id'))])
                if not act_brand:
                    data = {
                        'name': brand.get('name'),
                        'omna_brand_id': brand.get('id'),
                        'integration_id': self.integration_id.id
                    }
                    act_brand = brand_obj.with_context(synchronizing=True).create(data)
                else:
                    data = {'name': brand.get('name')}
                    act_brand.with_context(synchronizing=True).write(data)

            self.env.cr.commit()

            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)


