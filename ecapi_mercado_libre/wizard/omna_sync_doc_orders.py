# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class OmnaSyncDocOrders(models.TransientModel):
    _name = 'omna.sync_doc_orders_wizard'
    _inherit = 'omna.api'

    integration_id = fields.Many2one('omna.integration', 'Integration', domain=lambda self:[('company_id', '=', self.env.company.id)])
    number = fields.Char("Order Number")
    document_type = fields.Many2one('omna.doc.type', 'Document type', domain="[('sale_order.name', '=', number)]")
    # document_type = fields.Many2one('omna.doc.type', 'Document type')
    flag = fields.Boolean(string='Flag', required=False)


    def sync_doc_orders(self):
        try:
            limit = 25
            offset = 0
            requester = True
            orders = []
            orders_doc = []
            # https: // cenit.io / app / ecapi - v1 / integrations / {integration_id} / orders / {number} / doc / types

            sale = self.env['sale.order'].search([('name', '=', self.number)])
            if sale.state == 'cancel':
                raise ValidationError(('Cannot import order documents in canceled status'))

            if self.integration_id:
                response = self.get(
                    'integrations/%s/orders/%s/doc/types' % (
                        self.integration_id.integration_id, self.number),
                    {})
                orders = response.get('data')
                # orders.append(data)

                order_obj = self.env['omna.doc.type']
                for dt_order in orders:
                    act_doc_type = order_obj.search([('type', '=', dt_order.get('type')), ('sale_order', '=', sale.id)])
                    if not act_doc_type:
                        data = {
                            'type': dt_order.get('type'),
                            'title': dt_order.get('title'),
                            'sale_order': sale.id
                        }
                        act_doc_type = order_obj.with_context(synchronizing=True).create(data)
                return {
                    'name': 'Import doc of order',
                    'type': 'ir.actions.act_window',
                    'res_model': 'omna.sync_doc_orders_wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_number': self.number,
                        'default_flag': True,
                    }

                }
            else:
                # https: // cenit.io / app / ecapi - v1 / orders / {order_id} / doc / {doc_type}
                # https: // cenit.io / app / ecapi - v1 / orders / {order_id}
                response = self.get(
                    'orders/%s/doc/%s' % (sale.omna_id, self.document_type.type), {})
                # response = self.get(
                #     'orders/%s' % (sale.omna_id), {})

                orders_doc = response.get('data')

                order_doc_obj = self.env['omna.sale.doc']
                sale = self.env['sale.order'].search([('name', '=', self.number)])
                for dt_order in orders_doc:
                    act_doc_type = order_doc_obj.search([('omna_doc_id', '=', dt_order.get('id')), ('sale_order_doc', '=', sale.id)])
                    if not act_doc_type:
                        data = {
                            'file': dt_order.get('file'),
                            'mime_type': dt_order.get('mime_type'),
                            'title': dt_order.get('title'),
                            'document_type': dt_order.get('document_type'),
                            'sale_order_doc': sale.id,
                            'omna_doc_id': dt_order.get('id')
                        }
                        act_doc_type = order_doc_obj.with_context(synchronizing=True).create(data)
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload'
                }

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)




