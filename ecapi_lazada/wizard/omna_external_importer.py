# -*- coding: utf-8 -*-

import requests
import base64
import json
import logging
from datetime import datetime, timezone, time
from odoo.exceptions import ValidationError
from odoo import models, api, exceptions, fields

_logger = logging.getLogger(__name__)


class OmnaExternalImporter(models.TransientModel):
    _name = 'omna.external_importer_wizard'
    _inherit = 'omna.api'


    resource_type = fields.Selection([('categories', 'Categories'),
                                  ('brands', 'Brands'),
                                  ('products', 'Products'),
                                  ('orders', 'Orders')], 'Resource Type', required=True)
    integration_id = fields.Many2one('omna.integration', 'Integration', required=True)
    limit_date = fields.Date('Limit Date')




    def external_import_resources(self):
        try:
            # self.import_products()
            # https://cenit.io/app/ecapi-v1/integrations/{integration_id}/{resource_type}/import

            form_view_id = self.env.ref('ecapi_lazada.view_external_importer_wizard').id
            # date_formated = self.limit_date.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
            date_formated = self.limit_date.strftime('%Y-%m-%dT%H:%M:%SZ') if self.resource_type in ['products', 'orders'] else False
            temp_result = self.get('integrations/%s/%s/import' % (self.integration_id.integration_id, self.resource_type), {'updated_after': date_formated} if date_formated else {})
            self.env.user.notify_channel('info',
                                         'The task to import %s records from marketplace have been created, please go to "System\Tasks" to check out the task status.' % (self.resource_type,),
                                         "Information", True)
            return {
                'type': 'ir.actions.act_window',
                'name': 'Import Categories',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'omna.external_importer_wizard',
                'views': [[form_view_id, "form"]],
                'res_id': self.id,
                'context': self.env.context,
                'target': 'new',
            }

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
        pass



    # def background_import_resources(self):
    #     try:
    #         integration_result = self.env['omna.integration'].search([], limit=1)
    #         for item in ['categories', 'brands', 'products', 'orders']:
    #             temp_result = self.get('integrations/%s/%s/import' % (integration_result.integration_id, item))
    #             _logger.info('The task to import %s records from Prestashop to Cenit have been created, please go to "System\Tasks" to check out the task status.' % (item,))
    #
    #     except Exception as e:
    #         _logger.error(e)
    #     pass

