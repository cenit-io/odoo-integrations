# -*- coding: utf-8 -*-
from odoo import models, api, _, fields, exceptions
from odoo.exceptions import UserError


class OmnaUpdateProductInIntegration(models.TransientModel):
    _name = "omna.update.product.in.integration"
    _description = "Update Product ID in a Integration"

    integration_id = fields.Many2one('omna.integration', 'Integrations')

    def update_product(self):
        product = self.env['product.template'].search([('id', '=', self._context.get('active_id'))], limit=1)
        external = self.env['omna.template.integration.external.id'].search(
            [('product_template_id', '=', product.id),
             ('integration_id', '=', self.integration_id.id)], limit=1)
        categ = None
        brand = None
        # if product.categ_id:
        #     categ = self.env['product.category'].browse(product.categ_id.id)
        # if product.brand_id:
        #     brand = self.env['product.brand'].browse(product.brand_id.id)
        data = {
            'name': product.name,
            'price': product.list_price,
            'description': product.description,
            # 'category': categ.omna_category_id,
            # 'brand':brand.omna_brand_id
        }
        response = self.post('products/%s' % external.id, {'data': data})
        if not response.get('data').get('id'):
            raise exceptions.AccessError(_("Error trying to update products in Ecapi's API."))
