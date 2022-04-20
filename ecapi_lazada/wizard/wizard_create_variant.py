# -*- coding: utf-8 -*-
import json
from odoo import models, api, _, fields
from odoo.exceptions import ValidationError
from odoo.exceptions import *


class WizardCreateVariant(models.TransientModel):
    _name = "wizard.create.variant"
    _description = "Create a New Variant"


    lst_price = fields.Float('Price', default=0.00)
    name = fields.Char("Name")
    description = fields.Text('Description')
    default_code = fields.Char('Code')
    standard_price = fields.Float('Cost Price', default=0.00)
    # product_template_id = fields.Many2one('product.template', 'Product Template')
    quantity = fields.Integer('Quantity')
    weight = fields.Float('Weight (Kg)', digits=(16, 2))
    height = fields.Float('Height (Cm)', digits=(16, 2))
    length = fields.Float('Length (Cm)', digits=(16, 2))
    width = fields.Float('Width (Cm)', digits=(16, 2))
    content = fields.Char('Content')


    def create_variant(self):
        self.ensure_one()
        omna_variant_id = ''
        omna_template_id = ''
        fields_readed = self.read(['lst_price', 'name', 'description', 'default_code', 'standard_price',
                                   'quantity', 'weight', 'height', 'length', 'width', 'content'])[0]
        id, lst_price, name, description, default_code,\
        standard_price, quantity, weight, height, length, width, content = fields_readed.values()
        product_template = self.env['product.template'].browse(self.env.context.get('default_product_template_id'))
        # for product_template in product_template_ids:
        # if not omna_product_id:
        #     omna_product_id = product_template.omna_product_id

        if product_template.omna_product_id:
            data = {
                # 'name': name,
                # 'description': description,
                'sku': default_code,
                'price': lst_price,
                'original_price': standard_price,
                # 'quantity': quantity,
            }
            package_variant = dict([('weight', weight), ('height', height),
                                    ('length', length), ('width', width),
                                    ('content', content)])
            data.update({'package': package_variant})


            response = self.env['omna.api'].post('products/%s/variants' % product_template.omna_product_id, {'data': data})
            # response = self.env['omna.api'].post('products/%s/variants' % omna_product_id, data)
            if response.get('data').get('id'):
                product = response.get('data')
                omna_variant_id = product.get('id')
                # integrations = product_template.integration_ids.mapped('integration_ids')
                # integrations = product_template.integration_linked_ids.mapped('id')
                integrations = product_template.integration_linked_ids

                aux = []
                for item in integrations:
                    aux.append((0, 0, {'integration_ids': item.id,
                                       'remote_variant_id': "PENDING-PUBLISH-FROM-" + product.get('id'),
                                       'delete_from_integration': True}))


                list_variant = []

                product_attribute = self.env['product.attribute'].create({
                    'name': 'identifier',
                    'create_variant': 'dynamic'
                })

                product_attribute_value = self.env['product.attribute.value'].create({
                    'name': omna_variant_id,
                    'attribute_id': product_attribute.id})

                product_template_attribute_line = self.env['product.template.attribute.line'].create({
                    'product_tmpl_id': product_template.id,
                    'attribute_id': product_attribute.id,
                    'value_ids': [(4, product_attribute_value.id)],
                    'product_template_value_ids': [(0, 0, {
                        'name': omna_variant_id,
                        'product_attribute_value_id': product_attribute_value.id,
                    })],
                    # 'value_ids': [(6, 0, 'product_attribute_value')]
                })

                list_variant.append(product_template_attribute_line.product_template_value_ids.id)


                p = self.env['product.product'].with_context(create_product_product=True).create({
                        'name': name,
                        # 'description': description,
                        'custom_description': description,
                        'lst_price': product.get('price'),
                        'default_code': product.get('sku'),
                        'standard_price': product.get('original_price'),
                        'quantity': product.get('quantity'),
                        'omna_variant_id': product.get('id'),
                        'product_tmpl_id': product_template.id,
                        'variant_integrations_data': json.dumps(product.get('integrations'), separators=(',', ':')),
                        'product_template_attribute_value_ids': [(6, 0, list_variant)],
                        'category_ids': False,
                        'brand_ids': False,
                        'integration_linked_ids': [(6, 0, integrations.ids)],
                        'integration_ids': aux,
                        # 'integration_ids': [(6, 0, integration_ids)],
                        'peso': width,
                        'alto': height,
                        'longitud': length,
                        'ancho': width,
                        'contenido': content
                })


                if integrations:
                    data2 = {
                        'integration_ids': integrations.mapped('integration_id'),
                    }
                    result = self.env['omna.api'].put('products/%s/variants/%s/link' %(product_template.omna_product_id, omna_variant_id), {'data':data2})
                    self.env.user.notify_channel('warning', _(
                        'The task to export the order have been created, please go to "System\Tasks" to check out the task status.'),
                                                 _("Information"), True)

    def category_tree(self, arr, parent_id, category_id, integration_id, category_obj, list_category):
        # integration_id = self.env['omna.integration'].search([('name', '=', integration_category_name)])
        if len(arr) == 1:
            name = arr[0]
            c = category_obj.search(['|', ('omna_category_id', '=', category_id), '&',
                                     ('name', '=', name), ('parent_id', '=', parent_id),
                                     ('integration_id', '=', integration_id)], limit=1)
            if not c:
                c = category_obj.create({'name': name, 'omna_category_id': category_id,
                                         'parent_id': parent_id,
                                         'integration_id': integration_id})

            else:
                c.write({'name': name, 'parent_id': parent_id})

            list_category.append(c.id)
            return list_category

        elif len(arr) > 1:
            name = arr[0]
            c = category_obj.search(
                [('name', '=', name), ('integration_category_name', '=', integration_id)], limit=1)
            if not c:
                c = category_obj.create(
                    {'name': name, 'parent_id': parent_id, 'integration_category_name': integration_id})

            list_category.append(c.id)
            self.category_tree(arr[1:], c.id if c else False, category_id, integration_id, category_obj,
                               list_category)


