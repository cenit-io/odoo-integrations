# -*- coding: utf-8 -*-
from odoo import models, api, _, fields, exceptions
from odoo.exceptions import UserError


class OmnaUpdateVariantInIntegration(models.TransientModel):
    _name = "omna.update.variant.in.integration"
    _description = "Update Variant ID in a Integration"


    # external_id = fields.Char(u"External Product Id")
    # external_variant_id = fields.Char(u"External Variant Id")
    integration_id = fields.Many2one('omna.integration', 'Integrations', domain=lambda self:[('company_id', '=', self.env.company.id)])

    def update_variant(self):
        product = self.env['product.product'].search([('id', '=', self._context.get('active_id'))], limit=1)
        variant_external_id = self.env['omna.template.integration.external.id'].search(
            [('product_template_id', '=', product.id), ('integration_id', '=', self.integration_id.id)], limit=1)
        if product:
            template = self.env['product.template'].search([('id', '=', product.product_tmpl_id.id)], limit=1)
            product_external_id = self.env['omna.template.integration.external.id'].search(
                [('product_template_id', '=', template.id), ('integration_id', '=', self.integration_id.id)], limit=1)
            categ = None
            brand = None
            # if product.categ_id:
            #     categ = self.env['product.category'].browse(product.categ_id.id)
            # if product.brand_id:
            #     brand = self.env['product.brand'].browse(product.brand_id.id)
            data = {
                'name': product.name,
                'description': product.description,
                'price': product.lst_price,
                'sku': product.default_code,
                'quantity': product.quantity,
                'cost_price': product.standard_price,
                # 'category': categ.omna_category_id,
                # 'brand': brand.omna_brand_id
            }
            response = self.post('integrations/%s/products/%s/variants/%s' % (self.integration_id.id,
                                                                              product_external_id.id_external,
                                                                              variant_external_id.id_external),
                                 {'data': data})
            if not response.get('data').get('id'):
                raise exceptions.AccessError(_("Error trying to update products in Ecapi's API."))