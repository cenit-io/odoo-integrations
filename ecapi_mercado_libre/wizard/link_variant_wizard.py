# -*- coding: utf-8 -*-

import logging, odoo
from datetime import datetime, timezone
import dateutil.parser
from odoo import models, api, exceptions, fields, _
import pytz

_logger = logging.getLogger(__name__)


class LinkVariantWizard(models.TransientModel):
    _name = 'link.variant.wizard'
    _inherit = 'omna.api'



    omna_integration_id = fields.Many2one('omna.integration', 'Integration to Link', required=True, domain=lambda self:[('company_id', '=', self.env.company.id)])
    state = fields.Selection([('linked', 'LINKED'), ('unlinked', 'UNLINKED')])


    @api.onchange('omna_integration_id')
    def _onchange_omna_integration_id(self):
        # product_template_obj = self.env['product.template']
        product_product_obj = self.env['product.product']
        # variant_integration_obj = self.env['omna.integration_variant']
        # product = product_template_obj.search([('id', '=', self.env.context.get('default_product_template_id'))])
        variant = product_product_obj.search([('id', '=', self.env.context.get('active_id'))])
        # result = variant_integration_obj.search([('integration_ids', '=', self.omna_integration_id.id), ('product_product_id', '=', variant.id)]).ids
        if variant.integration_ids:
            self.state = 'linked'
        else:
            self.state = 'unlinked'


    def action_link_variant(self):
        # Agregar validacion para que no se intente linkear con una integracion que ya tenga linkeada.
        try:
            product_template_obj = self.env['product.template']
            product_product_obj = self.env['product.product']
            # variant_integration_obj = self.env['omna.integration_variant']
            integrations = [self.omna_integration_id.integration_id]
            data = {
                'data': {
                    'integration_ids': integrations,
                }
            }
            # https: // cenit.io / app / ecapi - v1 / products / {product_id} / variants / {variant_id}
            product = product_template_obj.search([('id', '=', self.env.context.get('default_product_template_id'))])
            variant = product_product_obj.search([('id', '=', self.env.context.get('active_id'))])
            # route = 'products/%s/variants/%s/link' % (product.omna_product_id, variant.omna_variant_id)
            # response = self.put(route, data)


            # result_integration = None
            # for integration in response.get('integrations'):
            #     if integration.get('id') == self.omna_integration_id.integration_id:
            #         result_integration = integration

            # variant_integration_obj.create({
            #     'product_product_id': product.id,
            #     'integration_ids': self.omna_integration_id.id,
            #     # 'remote_variant_id': integration.get('variant').get('remote_variant_id'),
            #     'remote_variant_id': "PENDING-PUBLISH-FROM-" + variant.omna_variant_id,
            #     'delete_from_integration': True,
            #
            # })

            val_update = {'integration_ids': [(0, 0, {'integration_ids': self.omna_integration_id.id,
                                         'remote_variant_id': "PENDING-PUBLISH-FROM-" + variant.omna_variant_id,
                                         'delete_from_integration': True})],
             'integration_linked_ids': [(4, self.omna_integration_id.id)]}

            variant.with_context(synchronizing=True, integrations=integrations).write(val_update)
            # self.product_template_id.write({'integration_linked_ids': [(4, self.integration_ids.id)]})
            self.env.cr.commit()
            return True
        except Exception as e:
            _logger.error(e)
            raise exceptions.ValidationError(e)
            # raise exceptions.AccessError(_("Error trying to update variant products in Omna's API."))
        return {'type': 'ir.actions.act_window_close'}



    def action_unlink_variant(self):
        pass
        # # Agregar validacion para que no se intente deslinkear con una integracion que ya tenga deslinkeada.
        # try:
        #     product_template_obj = self.env['product.template']
        #     product_product_obj = self.env['product.product']
        #     # variant_integration_obj = self.env['omna.integration_variant']
        #     integrations = [self.omna_integration_id.integration_id]
        #     data = {
        #         'data': {
        #             'integration_ids': integrations,
        #             'delete_from_integration': True
        #         }
        #     }
        #     # https: // cenit.io / app / ecapi - v1 / products / {product_id} / variants / {variant_id}
        #     product = product_template_obj.search([('id', '=', self.env.context.get('default_product_template_id'))])
        #     variant = product_product_obj.search([('id', '=', self.env.context.get('active_id'))])
        #     integrated = variant_integration_obj.search([('product_product_id', '=', variant.id), ('integration_ids', '=', self.omna_integration_id.id)])
        #     route = 'products/%s/variants/%s/link' % (product.omna_product_id, variant.omna_variant_id)
        #     response = self.delete(route, data)
        #     integrated.unlink()
        #     variant.with_context(synchronizing=True).write({'integration_linked_ids': [(3, self.omna_integration_id.id)]})
        #     # variant.write({'variant_integration_ids': [(3, self.omna_integration_id.id)]})
        #     self.env.cr.commit()
        #     return True
        # except Exception as e:
        #     _logger.error(e)
        #     raise exceptions.ValidationError(e)
        #     # raise exceptions.AccessError(_("Error trying to update variant products in Omna's API."))
        # return {'type': 'ir.actions.act_window_close'}
