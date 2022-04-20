# -*- coding: utf-8 -*-

import odoo
from datetime import *
from odoo import models, fields, api, exceptions, modules, tools, _
from odoo.exceptions import UserError
from odoo.tools.image import image_data_uri
from odoo.tools import float_compare, pycompat
from odoo.tools import ImageProcess
import dateutil.parser
import werkzeug
import pytz
import json
import os
import base64
import logging
import time
import threading
import string
import random
import math
import hmac
import hashlib
from requests_oauthlib import OAuth1
import requests


_logger = logging.getLogger(__name__)


def omna_id2real_id(omna_id):
    if omna_id and isinstance(omna_id, str) and len(omna_id.split('-')) == 2:
        res = [bit for bit in omna_id.split('-') if bit]
        return res[1]
    return omna_id

def truncate(numero, cifras):
    posiciones = pow(10.0, cifras)
    return math.trunc(posiciones * numero) / posiciones



class OmnaIntegration(models.Model):
    _name = 'omna.integration'
    _inherit = ['omna.api']

    @api.model
    def _get_integrations_channel_selection(self):
        try:
            response = self.get('available/integrations/channels', {})
            selection = []
            for channel in list(filter(lambda d: d['group'] == 'Lazada', response.get('data'))):
            # for channel in response.get('data'):
                selection.append((channel.get('name'), channel.get('title')))
            return selection
        except Exception as e:
            return []

    @api.model
    def _current_tenant(self):
        current_tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)],
                                                        limit=1)
        if current_tenant:
            return current_tenant.id
        else:
            return None

    omna_tenant_id = fields.Many2one('omna.tenant', 'Tenant', required=True, default=_current_tenant)
    name = fields.Char('Name', required=True)
    channel = fields.Selection(selection=_get_integrations_channel_selection, string='Channel', required=True)
    integration_id = fields.Char(string='Integration ID', required=True, index=True)
    authorized = fields.Boolean('Authorized', required=True, default=False)
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        "Image", attachment=True,
        help="This field holds the image used as image for the product, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized image", attachment=True,
        help="Medium-sized image of the product. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved, "
             "only when the image exceeds one of those sizes. Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized image", attachment=True,
        help="Small-sized image of the product. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")

    @api.model
    def _get_logo(self, channel):
        # image_path = modules.get_module_resource('mail', 'static/src/img', 'groupdefault.png')
        # return base64.b64encode(open(image_path, 'rb').read())
        if 'Lazada' in channel:
            logo = modules.get_module_resource('ecapi_lazada', 'static/src/img', 'lazada_logo.png')

        elif 'Qoo10' in channel:
            logo = modules.get_module_resource('ecapi_lazada', 'static/src/img', 'qoo10_logo.png')

        elif 'Shopee' in channel:
            logo = modules.get_module_resource('ecapi_lazada', 'static/src/img', 'shopee_logo.png')

        elif 'Shopify' in channel:
            logo = modules.get_module_resource('ecapi_lazada', 'static/src/img', 'shopify_logo.png')

        elif 'MercadoLibre' in channel:
            logo = modules.get_module_resource('ecapi_lazada', 'static/src/img', 'mercadolibre_logo.png')

        elif 'Prestashop' in channel:
            logo = modules.get_module_resource('ecapi_lazada', 'static/src/img', 'prestashop_logo.png')

        else:
            logo = modules.get_module_resource('ecapi_lazada', 'static/src/img', 'marketplace_placeholder.png')

        return logo

    @api.model
    def create(self, vals_list):

        if not vals_list.get('image'):
            path = self._get_logo(vals_list['channel'])
            vals_list['image'] = base64.b64encode(open(path, 'rb').read())

        image = ImageProcess(vals_list['image'])

        vals_list['image'] = image.resize(max_width=1024, max_height=1024).image_base64(output_format='png')
        vals_list['image_medium'] = image.resize(max_width=128, max_height=128).image_base64(output_format='png')
        vals_list['image_small'] = image.resize(max_width=64, max_height=64).image_base64(output_format='png')

        if not self._context.get('synchronizing'):
            self.check_access_rights('create')
            data = {
                'name': vals_list['name'],
                'channel': vals_list['channel']
            }

            response = self.post('integrations', {'data': data})
            if response.get('data').get('id'):
                vals_list['integration_id'] = response.get('data').get('id')
                return super(OmnaIntegration, self).create(vals_list)
            else:
                raise exceptions.AccessError(_("Error trying to push integration to Omna's API."))
        else:
            return super(OmnaIntegration, self).create(vals_list)

    def unlink(self):
        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        params = {
            "data": {
                "delete_from_integration": False
            }
        }
        for rec in self:
            integration_response = rec.delete('integrations/%s' % rec.integration_id)
        return super(OmnaIntegration, self).unlink()

    def unauthorize(self):
        for integration in self:
            response = self.delete('integrations/%s/authorize' % integration.integration_id)
        return self.write({'authorized': False})

    def authorize(self):
        self.ensure_one()
        omna_api_url = self.env['ir.config_parameter'].sudo().get_param(
            "ecapi_lazada.cenit_url", default='https://cenit.io/app/ecapi-v1'
        )
        redirect = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url') + '/omna/integrations/authorize/' + self.integration_id
        path = 'integrations/%s/authorize' % self.integration_id

        config = self.get_config()
        payload = {}
        timestamp = datetime.now(timezone.utc)
        payload['token'] = config['cenit_user_token']
        payload['timestamp'] = int(datetime.timestamp(timestamp) * 1000)
        payload['redirect_uri'] = redirect
        chars = (json.dumps(payload, separators=(',', ':')).replace('"', '')).replace("'", '')
        data_msg = [char for char in chars]
        data_msg.sort()
        msg = path + ''.join(data_msg)
        signature = hmac.new(bytes(config['cenit_user_secret'], 'utf-8'), msg=bytes(msg, 'utf-8'), digestmod=hashlib.sha256).hexdigest()
        payload['hmac'] = signature
        authorize_url = '%s/%s?%s' % (omna_api_url, path, werkzeug.urls.url_encode(payload))

        return {
            'type': 'ir.actions.act_url',
            'url': authorize_url,
            'target': 'self'
        }




class OmnaWebhook(models.Model):
    _name = 'omna.webhook'
    _inherit = 'omna.api'
    _rec_name = 'topic'

    @api.model
    def _get_webhook_topic_selection(self):
        try:
            response = self.get('webhooks/topics', {})
            selection = []
            for topic in response.get('data'):
                selection.append((topic.get('topic'), topic.get('title')))
            return selection
        except Exception as e:
            return []

    @api.model
    def _current_tenant(self):
        current_tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)],
                                                        limit=1)
        if current_tenant:
            return current_tenant.id
        else:
            return None

    omna_tenant_id = fields.Many2one('omna.tenant', 'Tenant', required=True, default=_current_tenant)
    omna_webhook_id = fields.Char("Webhooks identifier in OMNA", index=True)
    topic = fields.Selection(selection=_get_webhook_topic_selection, string='Topic', required=True)
    address = fields.Char('Address', required=True)
    integration_id = fields.Many2one('omna.integration', 'Integration', required=True)

    @api.model
    def create(self, vals_list):
        if not self._context.get('synchronizing'):
            integration = self.env['omna.integration'].search([('id', '=', vals_list['integration_id'])], limit=1)
            data = {
                'integration_id': integration.integration_id,
                'topic': vals_list['topic'],
                'address': vals_list['address'],
            }
            response = self.post('webhooks', {'data': data})
            if response.get('data').get('id'):
                vals_list['omna_webhook_id'] = response.get('data').get('id')
                return super(OmnaWebhook, self).create(vals_list)
            else:
                raise exceptions.AccessError(_("Error trying to push webhook to Omna's API."))
        else:
            return super(OmnaWebhook, self).create(vals_list)

    def write(self, vals):
        self.ensure_one()
        if not self._context.get('synchronizing'):
            if 'integration_id' in vals:
                integration = self.env['omna.integration'].search([('id', '=', vals['integration_id'])], limit=1)
            else:
                integration = self.env['omna.integration'].search([('id', '=', self.integration_id.id)], limit=1)
                data = {
                    'address': vals['address'] if 'address' in vals else self.address,
                    'integration_id': integration.integration_id,
                    'topic': vals['topic'] if 'topic' in vals else self.topic
                }
            response = self.post('webhooks/%s' % self.omna_webhook_id, {'data': data})
            if response.get('data').get('id'):
                vals['omna_webhook_id'] = response.get('data').get('id')
                return super(OmnaWebhook, self).write(vals)
            else:
                raise exceptions.AccessError(_("Error trying to update webhook in Omna's API."))
        else:
            return super(OmnaWebhook, self).write(vals)

    def unlink(self):
        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        for rec in self:
            response = rec.delete('webhooks/%s' % rec.omna_webhook_id)
        return super(OmnaWebhook, self).unlink()



class OmnaFlow(models.Model):
    _name = 'omna.flow'
    _inherit = 'omna.api'
    _rec_name = 'type'

    @api.model
    def _get_flow_types(self):
        try:
            response = self.get('flows/types', {})
            selection = []
            for type in response.get('data'):
                selection.append((type.get('type'), type.get('title')))
            return selection
        except Exception as e:
            return []

    @api.model
    def _current_tenant(self):
        current_tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)],
                                                        limit=1)
        if current_tenant:
            return current_tenant.id
        else:
            return None

    omna_tenant_id = fields.Many2one('omna.tenant', 'Tenant', required=True, default=_current_tenant)
    integration_id = fields.Many2one('omna.integration', 'Integration', required=True)
    type = fields.Selection(selection=_get_flow_types, string='Type', required=True)
    start_date = fields.Datetime("Start Date", help='Select date and time')
    end_date = fields.Date("End Date")
    days_of_week = fields.Many2many('omna.filters', 'omna_flow_days_of_week_rel', 'flow_id', 'days_of_week_id',
                                    domain=[('type', '=', 'dow')])
    weeks_of_month = fields.Many2many('omna.filters', 'omna_flow_weeks_of_month_rel', 'flow_id', 'weeks_of_month_id',
                                      domain=[('type', '=', 'wom')])
    months_of_year = fields.Many2many('omna.filters', 'omna_flow_months_of_year_rel', 'flow_id', 'months_of_year_id',
                                      domain=[('type', '=', 'moy')])
    omna_id = fields.Char('OMNA Workflow ID', index=True)
    active = fields.Boolean('Active', default=True, readonly=True)

    def start(self):
        for flow in self:
            self.get('flows/%s/start' % flow.omna_id, {})
        self.env.user.notify_channel('warning', _(
            'The task to execute the workflow have been created, please go to "System\Tasks" to check out the task status.'),
                                     _("Information"), True)
        return {'type': 'ir.actions.act_window_close'}

    def toggle_status(self):
        for flow in self:
            self.get('flows/%s/toggle/scheduler/status' % flow.omna_id, {})

        self.env.user.notify_channel('warning', _('The workflow\'s status have been changed.'), _("Information"), True)
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def create(self, vals):
        if not self._context.get('synchronizing'):
            integration = self.env['omna.integration'].search([('id', '=', vals.get('integration_id'))], limit=1)
            data = {
                "integration_id": integration.integration_id,
                "type": vals.get('type'),
                "scheduler": {}
            }

            if 'start_date' in vals:
                start_date = datetime.datetime.strptime(vals.get('start_date'), "%Y-%m-%d %H:%M:%S")
                data['scheduler']['start_date'] = start_date.date().strftime("%Y-%m-%d")
                data['scheduler']['time'] = start_date.time().strftime("%H:%M")
            if 'end_date' in vals:
                end_date = datetime.datetime.strptime(vals.get('end_date'), "%Y-%m-%d")
                data['scheduler']['end_date'] = end_date.strftime("%Y-%m-%d")
            if 'days_of_week' in vals:
                dow = []
                days = self.env['omna.filters'].search(
                    [('type', '=', 'dow'), ('id', 'in', vals.get('days_of_week')[0][2])])
                for day in days:
                    dow.append(day.name)
                data['scheduler']['days_of_week'] = dow
            if 'weeks_of_month' in vals:
                wom = []
                weeks = self.env['omna.filters'].search(
                    [('type', '=', 'wom'), ('id', 'in', vals.get('weeks_of_month')[0][2])])
                for week in weeks:
                    wom.append(week.name)
                data['scheduler']['weeks_of_month'] = wom
            if 'months_of_year' in vals:
                moy = []
                months = self.env['omna.filters'].search(
                    [('type', '=', 'moy'), ('id', 'in', vals.get('months_of_year')[0][2])])
                for month in months:
                    moy.append(month.name)
                data['scheduler']['months_of_year'] = moy

            response = self.post('flows', {'data': data})
            if 'id' in response.get('data'):
                vals['omna_id'] = response.get('data').get('id')
                return super(OmnaFlow, self).create(vals)
            else:
                raise exceptions.AccessError(_("Error trying to push the workflow to Omna."))
        else:
            return super(OmnaFlow, self).create(vals)

    def write(self, vals):
        self.ensure_one()
        if not self._context.get('synchronizing'):
            if 'type' in vals:
                raise UserError(
                    "You cannot change the type of a worflow. Instead you should delete the current workflow and create a new one of the proper type.")
            if 'integration_id' in vals:
                raise UserError(
                    "You cannot change the integration of a worflow. Instead you should delete the current workflow and create a new one of the proper type.")

            data = {
                "scheduler": {}
            }

            if 'start_date' in vals:
                start_date = datetime.datetime.strptime(vals.get('start_date'), "%Y-%m-%d %H:%M:%S")
                data['scheduler']['start_date'] = start_date.date().strftime("%Y-%m-%d")
                data['scheduler']['time'] = start_date.time().strftime("%H:%M")
            if 'end_date' in vals:
                end_date = datetime.datetime.strptime(vals.get('end_date'), "%Y-%m-%d")
                data['scheduler']['end_date'] = end_date.strftime("%Y-%m-%d")
            if 'days_of_week' in vals:
                dow = []
                days = self.env['omna.filters'].search(
                    [('type', '=', 'dow'), ('id', 'in', vals.get('days_of_week')[0][2])])
                for day in days:
                    dow.append(day.name)
                data['scheduler']['days_of_week'] = dow
            if 'weeks_of_month' in vals:
                wom = []
                weeks = self.env['omna.filters'].search(
                    [('type', '=', 'wom'), ('id', 'in', vals.get('weeks_of_month')[0][2])])
                for week in weeks:
                    wom.append(week.name)
                data['scheduler']['weeks_of_month'] = wom
            if 'months_of_year' in vals:
                moy = []
                months = self.env['omna.filters'].search(
                    [('type', '=', 'moy'), ('id', 'in', vals.get('months_of_year')[0][2])])
                for month in months:
                    moy.append(month.name)
                data['scheduler']['months_of_year'] = moy

            response = self.post('flows/%s' % self.omna_id, {'data': data})
            if 'id' in response.get('data'):
                return super(OmnaFlow, self).write(vals)
            else:
                raise exceptions.AccessError(_("Error trying to update the workflow in Omna."))
        else:
            return super(OmnaFlow, self).write(vals)

    def unlink(self):
        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        for flow in self:
            flow.delete('flows/%s' % flow.omna_id)
        return super(OmnaFlow, self).unlink()



class OmnaIntegrationProduct(models.Model):
    _name = 'omna.integration_product'
    _inherit = 'omna.api'
    _rec_name = 'integration_ids'


    def _get_product_template_id(self):
        return self.env.context.get('default_product_template_id', False)


    def _compute_state(self):
        for item in self:
            if item.integration_ids in item.product_template_id.integration_linked_ids:
                item.state = 'linked'
            else:
                item.state = 'unlinked'


    @api.depends('active_on_sale')
    def _compute_marketplace_state(self):
        for item in self:
            if item.active_on_sale:
                item.marketplace_state = 'published'
            else:
                item.marketplace_state = 'unpublished'



    product_template_id = fields.Many2one('product.template', 'Product', required=True, ondelete='cascade', default=lambda self: self.env.context.get('default_product_template_id', False))

    integration_ids = fields.Many2one('omna.integration', 'OMNA Integration', required=True, ondelete='cascade')
    link_with_its_variants = fields.Selection([
        ('NONE', 'NONE'),
        ('SELECTED', 'SELECTED'),
        ('NEW', 'NEW'),
        ('ALL', 'ALL')], default='ALL', required=True)
    delete_from_integration = fields.Boolean("Delete from Integration", default=True,
                                             help="Set whether the product should be removed from the remote integration source.")
    state = fields.Selection([('linked', 'LINKED'), ('unlinked', 'UNLINKED')], default='unlinked', compute='_compute_state')
    remote_product_id = fields.Char("Published identifier in OMNA", index=True)
    marketplace_state = fields.Selection([('published', 'PUBLISHED'), ('unpublished', 'UNPUBLISHED')], compute='_compute_marketplace_state', store=True, string="On Marketplace")
    active_on_sale = fields.Boolean("Active On Sale", default=False)



    @api.model
    def create(self, vals_list):
        res = super(OmnaIntegrationProduct, self).create(vals_list)
        return res


    def unlink(self):
        return super(OmnaIntegrationProduct, self).unlink()


    def action_link(self):
        try:
            integrations = [self.integration_ids.integration_id]
            data = {
                'data': {
                    'integration_ids': integrations,
                    'link_with_its_variants': self.link_with_its_variants
                }
            }

            response = self.put('products/%s/link' % self.product_template_id.omna_product_id, data)

            self.product_template_id.with_context(synchronizing=True).write({'integration_linked_ids': [(4, self.integration_ids.id)]})

            self.write({'remote_product_id': "PENDING-PUBLISH-FROM-" + self.product_template_id.omna_product_id})
            if self.link_with_its_variants == "ALL":
                create_value_list = []
                for item in self.product_template_id.product_variant_ids:
                    if item.omna_variant_id != False:
                        if not self.integration_ids.id in item.integration_ids.integration_ids.ids:
                            create_value_list.append({'integration_ids': self.integration_ids.id,
                                                  'remote_variant_id': "PENDING-PUBLISH-FROM-" + item.omna_variant_id,
                                                  'delete_from_integration': True,
                                                  'product_product_id': item.id})
                            item.with_context(synchronizing=True).write({'integration_linked_ids': [(4, self.integration_ids.id)]})

                if len(create_value_list) != 0:
                    self.env['omna.integration_variant'].create(create_value_list)



            # if not self.product_template_id.property_ids:
            #     temp_product = {"data": {"properties": [{"id": "category_id", "value": self.product_template_id.categ_id.omna_category_id}]}}
            #     temp_product["data"]["properties"].append(
            #         {"id": "category_id", "value": self.product_template_id.categ_id.omna_category_id})
            #
            #     response2 = self.post('integrations/%s/products/%s' % (
            #     self.integration_ids.integration_id, self.product_template_id.omna_product_id), temp_product)
            #     # https://cenit.io/app/ecapi-v1/integrations/{integration_id}/categories/{category_id}/product/properties
            #     prop_response = self.get('integrations/%s/categories/%s/product/properties' % (self.integration_ids.integration_id, self.product_template_id.categ_id.omna_category_id,))
            #     list_properties = prop_response.get('data')
            #     list_data = []
            #     for item in list_properties:
            #         if not item.get('id') in ['category_id', 'brand']:
            #             list_data.append({
            #                 'property_name': item.get('id'),
            #                 'property_type': item.get('input_type'),
            #                 'integration_id': self.integration_ids.id,
            #                 'property_label': item.get('label'),
            #                 'product_template_id': self.product_template_id.id,
            #                 'property_required': item.get('required'),
            #                 'value_option_ids': [
            #                     (0, 0, {'option_value': X, 'option_label': X}) if isinstance(X, str) else (
            #                     0, 0, {'option_value': X.get('value'), 'option_label': X.get('label')}) for X in
            #                     item.get('options')],
            #             })
            #     self.env['properties.values.product'].create(list_data)

            # # https://cenit.io/app/ecapi-v1/products/{product_id}/stock/items
            # query_result = self.get('products/%s/stock/items' % (self.product_template_id.omna_product_id,))
            # list_data = query_result.get('data')
            # list_aux = []
            # for query_data in list_data:
            #     stock_location_id = self.env['stock.location'].search([('omna_id', '=', query_data.get('stock_location').get('id'))])
            #     stock_data = {
            #         'omna_id': query_data.get('id', False),
            #         'integration_id': self.integration_ids.id,
            #         'stock_location_id': stock_location_id.id,
            #         'product_product_name': "[%s]" % query_data.get('product').get('name'),
            #         'product_template_name': query_data.get('product').get('name'),
            #         # 'product_product_omna_id': product.get('product').get('variant').get('id'),
            #         'product_template_omna_id': self.product_template_id.omna_product_id,
            #         'count_on_hand': query_data.get('count_on_hand', 0),
            #     }
            #     list_aux.append(stock_data)
            #
            # self.env['omna.stock.items'].create(list_aux)
            self.env.cr.commit()
            self.env.user.notify_channel('info', _(
                'The task to link product with integration have been created, please go to "System\Tasks" to check out the task status.'),
                                         _("Information"), True)
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)


    def action_unlink(self):
        try:
            integrations = [self.integration_ids.integration_id]
            data_1 = {
                "data": {
                    "variant_ids": self.product_template_id.product_variant_ids.mapped("omna_variant_id"),
                    "integration_ids": integrations,
                    "delete_from_integration": True
                }
            }

            data = {
                'data': {
                    'integration_ids': integrations,
                    'delete_from_integration': self.delete_from_integration
                }
            }

            if self.product_template_id.product_variant_ids:
                response_1 = self.delete('products/%s/variants/link' % self.product_template_id.omna_product_id, data_1)
            response_2 = self.delete('products/%s/link' % self.product_template_id.omna_product_id, data)

            self.product_template_id.with_context(synchronizing=True).write({'integration_linked_ids': [(3, self.integration_ids.id)]})
            self.write({'active_on_sale': False})


            if self.link_with_its_variants == "ALL":
                ids_list = self.product_template_id.product_variant_ids.ids
                result = self.env['omna.integration_variant'].search([('product_product_id', 'in', ids_list), ('integration_ids', '=', self.integration_ids.id)])
                result.unlink()
                self.product_template_id.product_variant_ids.with_context(synchronizing=True).write({'integration_linked_ids': [(3, self.integration_ids.id)]})

            self.env.cr.commit()

            self.env.user.notify_channel('info', _(
                'The task to unlink product with integration have been created, please go to "System\Tasks" to check out the task status.'),
                                         _("Information"), True)
        except Exception as e:
            _logger.error(e)
            # raise exceptions.AccessError(_("Error trying to update products in Omna's API."))
            raise exceptions.AccessError(e)


    def action_publish(self):
        self.write({'active_on_sale': True})

        data = {
            'name': self.product_template_id.name,
            'price': self.product_template_id.list_price,
            'description': self.product_template_id.description,
            'package': {'weight': self.product_template_id.peso,
                        'height': self.product_template_id.alto,
                        'length': self.product_template_id.longitud,
                        'width': self.product_template_id.ancho,
                        'content': "No definido dos ejemplo",
                        'overwrite': self.product_template_id.overwrite}
        }

        response1 = self.post('products/%s' % self.product_template_id.omna_product_id, {'data': data})

        temp_product = {
            "data": {
                "properties": [{"id": X.property_name, "value": X.property_stored_value} for X in self.product_template_id.property_ids]
            }
        }

        # temp_product["data"]["properties"].append({"id": "brand", "value": self.product_template_id.product_brand_id.omna_brand_id})
        temp_product["data"]["properties"].append({"id": "category_id", "value": self.product_template_id.categ_id.omna_category_id})

        response2 = self.post('integrations/%s/products/%s' % (self.integration_ids.integration_id, self.product_template_id.omna_product_id), temp_product)

        self.env.user.notify_channel('info', _(
            'The task to publish product on marketplace have been created, please go to "System\Tasks" to check out the task status.'),
                                     _("Information"), True)


    def action_unpublish(self):
        self.write({'active_on_sale': False})
        temp_product = {
            "data": {
                "properties": [
                    {
                        "id": "active",
                        "value": False
                    },
                    {
                        "id": "visibility",
                        "value": "none"
                    },
                    {
                        "id": "available_for_order",
                        "value": False
                    }
                ]
            }
        }

        response = self.post('integrations/%s/products/%s' % (self.integration_ids.integration_id, self.product_template_id.omna_product_id), temp_product)

        self.env.user.notify_channel('info', _(
            'The task to unpublish product on marketplace have been created, please go to "System\Tasks" to check out the task status.'),
                                     _("Information"), True)


    def action_update(self):
        # temp_product = {
        #     "data": {
        #         "properties": [
        #             {
        #                 "id": "category_id",
        #                 "value": self.product_template_id.categ_id.omna_category_id
        #             }
        #         ]
        #     }
        # }

        data = {
            'name': self.product_template_id.name,
            'price': self.product_template_id.list_price,
            'description': self.product_template_id.description,
            'package': {'weight': self.product_template_id.peso,
                        'height': self.product_template_id.alto,
                        'length': self.product_template_id.longitud,
                        'width': self.product_template_id.ancho,
                        'content': "No definido",
                        'overwrite': self.product_template_id.overwrite}
        }

        response1 = self.post('products/%s' % self.product_template_id.omna_product_id, {'data': data})

        if not self.product_template_id.property_ids:
            temp_01 = {"data": {"properties": [{"id": "category_id", "value": self.product_template_id.categ_id.omna_category_id}]}}

            self.post('integrations/%s/products/%s' % (self.integration_ids.integration_id, self.product_template_id.omna_product_id), temp_01)
            # https://cenit.io/app/ecapi-v1/integrations/{integration_id}/categories/{category_id}/product/properties
            prop_response = self.get('integrations/%s/categories/%s/product/properties' % (self.integration_ids.integration_id, self.product_template_id.categ_id.omna_category_id,))
            list_properties = prop_response.get('data')
            list_data = []
            for item in list_properties:
                # if not item.get('id') in ['category_id', 'brand']:
                if item.get('id') != 'category_id':
                    list_data.append({
                        'property_name': item.get('id'),
                        'property_type': item.get('input_type'),
                        'integration_id': self.integration_ids.id,
                        'property_label': item.get('label'),
                        'product_template_id': self.product_template_id.id,
                        'property_required': item.get('required'),
                        'value_option_ids': [
                            (0, 0, {'option_value': X, 'option_label': X}) if isinstance(X, str) else (
                                0, 0, {'option_value': X.get('value'), 'option_label': X.get('label')}) for X in
                            item.get('options')],
                    })
            self.env['properties.values.product'].create(list_data)
            self.env.cr.commit()

        else:
            temp_product = {
                "data": {
                    "properties": [{"id": X.property_name, "value": X.property_stored_value} for X in self.product_template_id.property_ids]
                }
            }

            # temp_product["data"]["properties"].append({"id": "brand", "value": self.product_template_id.product_brand_id.omna_brand_id})
            temp_product["data"]["properties"].append({"id": "brand", "value": "124213044"})
            temp_product["data"]["properties"].append({"id": "category_id", "value": self.product_template_id.categ_id.omna_category_id})

            response2 = self.post('integrations/%s/products/%s' % (self.integration_ids.integration_id, self.product_template_id.omna_product_id), temp_product)

            # new_price = 0
            #
            # if self.product_template_id.taxes_id.price_include:
            #     aux_price = self.product_template_id.omna_tax_id.amount + 100
            #     to_round = self.product_template_id.list_price / (aux_price / 100)
            #     formatted_string = str(truncate(to_round, 6))
            #     new_price = round(to_round, 5) if int(formatted_string[-1]) <= 5 else round(to_round, 6)
            # if not self.product_template_id.taxes_id.price_include:
            #     new_price = self.product_template_id.list_price


            # response2 = self.post('integrations/%s/products/%s' % (self.integration_ids.integration_id, self.product_template_id.omna_product_id), temp_product)

            # if not self.product_template_id.property_ids:
            #     list_properties = response2.get('data').get('integration').get('product').get('properties')
            #     list_data = []
            #     for item in list_properties:
            #         if not item.get('id') in ['category_id', 'brand']:
            #             list_data.append({
            #             'property_name': item.get('id'),
            #             'property_type': item.get('input_type'),
            #             'integration_id': self.integration_ids.id,
            #             'property_label': item.get('label'),
            #             'product_template_id': self.product_template_id.id,
            #             'property_required': item.get('required'),
            #             'value_option_ids': [(0, 0, {'option_value': X, 'option_label': X}) if isinstance(X, str) else (0, 0, {'option_value': X.get('value'), 'option_label': X.get('label')}) for X in item.get('options') ],
            #             })
            #     self.env['properties.values.product'].create(list_data)

            self.env['omna.integration_variant'].variant_update_ecommerce(self.integration_ids.integration_id, self.product_template_id, self.product_template_id.product_variant_ids)

            self.env.user.notify_channel('info', _(
                'The task to update all product data on marketplace have been created, please go to "System\Tasks" to check out the task status.'),
                                         _("Information"), True)



class OmnaIntegrationVariant(models.Model):
    _name = 'omna.integration_variant'
    _inherit = 'omna.api'
    _rec_name = 'integration_ids'


    def _get_product_product_id(self):
        return self.env.context.get('default_product_product_id', False)


    def _compute_state(self):
        for item in self:
            if item.integration_ids in item.product_product_id.integration_linked_ids:
                item.state = 'linked'
            else:
                item.state = 'unlinked'


    product_product_id = fields.Many2one('product.product', 'Product Variant', required=True, ondelete='cascade', default=lambda self: self.env.context.get('default_product_product_id', False))
    integration_ids = fields.Many2one('omna.integration', 'OMNA Integration', required=True, ondelete='cascade')
    link_with_its_variants = fields.Selection([
        ('NONE', 'NONE'),
        ('SELECTED', 'SELECTED'),
        ('NEW', 'NEW'),
        ('ALL', 'ALL')], default='ALL', required=True)
    delete_from_integration = fields.Boolean("Delete from Integration", default=True,
                                             help="Set whether the product should be removed from the remote integration source.")
    state = fields.Selection([('linked', 'LINKED'), ('unlinked', 'UNLINKED')], default='unlinked', compute='_compute_state')
    remote_variant_id = fields.Char("Published identifier in OMNA", index=True)


    @api.model
    def create(self, vals_list):
        res = super(OmnaIntegrationVariant, self).create(vals_list)
        return res


    def unlink(self):
        return super(OmnaIntegrationVariant, self).unlink()


    def launch_wizard_list(self):
        view_id = self.env.ref('ecapi_lazada.view_properties_values_wizard').id
        context = dict(
            self.env.context,
            integration_id=self.integration_ids.id,
            integration_product_id=self.id,
        )

        return {
            'name': 'Property List By Integrations',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'properties.values.wizard',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': context,
        }


    def action_link(self):
        try:
            integrations = [self.integration_ids.integration_id]
            data = {
                'data': {
                    'integration_ids': integrations,
                }
            }

            response = self.put('products/%s/variants/%s/link' % (self.product_product_id.product_tmpl_id.omna_product_id ,self.product_product_id.omna_variant_id), data)

            self.product_product_id.with_context(synchronizing=True).write({'integration_linked_ids': [(4, self.integration_ids.id)]})
            self.write({'remote_variant_id': "PENDING-PUBLISH-FROM-" + self.product_product_id.omna_variant_id})

            # https://cenit.io/app/ecapi-v1/products/{product_id}/variants/{variant_id}/stock/items
            query_result = self.get('products/%s/variants/%s/stock/items' % (self.product_product_id.product_tmpl_id.omna_product_id, self.product_product_id.omna_variant_id))
            list_data = query_result.get('data')
            list_aux = []
            for query_data in list_data:
                stock_location_id = self.env['stock.location'].search([('omna_id', '=', query_data.get('stock_location').get('id'))])
                stock_data = {
                    'omna_id': query_data.get('id', False),
                    'integration_id': self.integration_ids.id,
                    'stock_location_id': stock_location_id.id,
                    'product_product_name': "[%s]" % query_data.get('product').get('name'),
                    'product_template_name': query_data.get('product').get('name'),
                    'product_product_omna_id': self.product_product_id.omna_variant_id,
                    'product_template_omna_id': query_data.get('product').get('id'),
                    'count_on_hand': query_data.get('count_on_hand', 0),
                }
                list_aux.append(stock_data)

            self.env['omna.stock.items'].create(list_aux)
            self.env.cr.commit()

            self.env.user.notify_channel('info', _(
                'The task to link variant with integration have been created, please go to "System\Tasks" to check out the task status.'),
                                         _("Information"), True)
            return self
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(_("Error trying to update products in Omna's API."))


    def action_unlink(self):
        try:
            integrations = [self.integration_ids.integration_id]
            data = {
                'data': {
                    'integration_ids': integrations,
                    'delete_from_integration': self.delete_from_integration
                }
            }

            response = self.delete('products/%s/variants/%s/link' % (self.product_product_id.product_tmpl_id.omna_product_id ,self.product_product_id.omna_variant_id), data)

            self.product_product_id.with_context(synchronizing=True).write({'integration_linked_ids': [(3, self.integration_ids.id)]})
            self.env.cr.commit()
            self.env.user.notify_channel('info', _(
                'The task to unlink variant from integration have been created, please go to "System\Tasks" to check out the task status.'),
                                         _("Information"), True)

            return self
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(_("Error trying to update products in Omna's API."))


    def action_publish(self):

        data = {
            # 'price': self.product_product_id.price_extra + new_price,
            'price': self.product_product_id.price_extra + self.product_product_id.product_tmpl_id.list_price,
            'sku': self.product_product_id.default_code,
            'package': {'weight': self.product_product_id.peso,
                        'height': self.product_product_id.alto,
                        'length': self.product_product_id.longitud,
                        'width': self.product_product_id.ancho,
                        'content': "No definido"
                        }
        }

        response1 = self.post('products/%s/variants/%s' % (self.product_product_id.product_tmpl_id.omna_product_id, self.product_product_id.omna_variant_id), {'data': data})

        temp_product = {
            "data": {
                "properties": [{"id": X.property_name, "value": X.property_stored_value} for X in self.product_product_id.property_ids]
            }
        }

        temp_product["data"]["properties"].append({"id": "price_adjustment", "value": self.product_product_id.price_adjustment})
        temp_product["data"]["properties"].append({"id": "price_adjustment_type", "value": self.product_product_id.price_adjustment_type})

        response2 = self.post('integrations/%s/products/%s/variants/%s' % (self.integration_ids.integration_id, self.product_product_id.product_tmpl_id.omna_product_id, self.product_product_id.omna_variant_id), temp_product)


        self.env.user.notify_channel('info', _(
            'The task to publish product variant on marketplace have been created, please go to "System\Tasks" to check out the task status.'),
                                     _("Information"), True)


    def action_update_ecommerce(self):
        # temp = {
        #     "data": {
        #         "properties": [{"id": int(item.attribute_id.omna_attribute_id),
        #                         "value": int(item.product_attribute_value_id.omna_attribute_value_id)} for item in
        #                        self.product_product_id.product_template_attribute_value_ids]
        #     }
        # }

        if self.product_product_id.property_ids:
            self.action_publish()
        else:
            # temp = {
            #     # "variant_id": self.product_product_id.omna_variant_id,
            #     "properties": [
            #         {"id": "price_adjustment", "value": self.product_product_id.price_adjustment},
            #         {"id": "price_adjustment_type", "value": self.product_product_id.price_adjustment_type}]
            # }

            # new_price = 0
            #
            # if self.product_product_id.product_tmpl_id.taxes_id.price_include:
            #     aux_price = self.product_product_id.product_tmpl_id.omna_tax_id.amount + 100
            #     to_round = self.product_product_id.product_tmpl_id.list_price / (aux_price / 100)
            #     formatted_string = str(truncate(to_round, 6))
            #     new_price = round(to_round, 5) if int(formatted_string[-1]) <= 5 else round(to_round, 6)
            #
            # if not self.product_product_id.product_tmpl_id.taxes_id.price_include:
            #     new_price = self.product_product_id.product_tmpl_id.list_price

            data = {
                # 'price': self.product_product_id.price_extra + new_price,
                'price': self.product_product_id.price_extra + self.product_product_id.product_tmpl_id.list_price,
                'sku': self.product_product_id.default_code,
                'package': {'weight': self.product_product_id.peso,
                            'height': self.product_product_id.alto,
                            'length': self.product_product_id.longitud,
                            'width': self.product_product_id.ancho,
                            'content': "No definido"
                            }
            }

            response1 = self.post('products/%s/variants/%s' % (self.product_product_id.product_tmpl_id.omna_product_id, self.product_product_id.omna_variant_id), {'data': data})
            # response2 = self.post('integrations/%s/products/%s/variants/%s' % (self.integration_ids.integration_id, self.product_product_id.product_tmpl_id.omna_product_id, self.product_product_id.omna_variant_id), {'data': temp})

            if not self.product_product_id.property_ids:
                # https://cenit.io/app/ecapi-v1/integrations/{integration_id}/categories/{category_id}/product/properties
                prop_response = self.get('integrations/%s/categories/%s/variant/properties' % (self.integration_ids.integration_id, self.product_product_id.categ_id.omna_category_id))
                list_properties = prop_response.get('data')
                list_data = []
                for item in list_properties:
                    if not item.get('id') in ['category_id', 'brand']:
                        list_data.append({
                            'property_name': item.get('id'),
                            'property_type': item.get('input_type'),
                            'integration_id': self.integration_ids.id,
                            'property_label': item.get('label'),
                            'product_product_id': self.product_product_id.id,
                            'property_required': item.get('required'),
                            'value_option_ids': [
                                (0, 0, {'option_value': X, 'option_label': X}) if isinstance(X, str) else (
                                0, 0, {'option_value': X.get('value'), 'option_label': X.get('label')}) for X in
                                item.get('options')],
                        })
                self.env['properties.values.variant'].create(list_data)

            # list_properties = response2.get('data').get('integration').get('variant').get('properties')
            # list_data = []
            # for item in list_properties:
            #     if not item.get('id') in ['category_id', 'brand']:
            #         list_data.append({
            #             'property_name': item.get('id'),
            #             'property_type': item.get('input_type'),
            #             'integration_id': self.integration_ids.id,
            #             'property_label': item.get('label'),
            #             'product_product_id': self.product_product_id.id,
            #             'property_required': item.get('required'),
            #             'value_option_ids': [(0, 0, {'option_value': X, 'option_label': X}) if isinstance(X, str) else (0, 0, {'option_value': X.get('value'), 'option_label': X.get('label')}) for X in item.get('options') ],
            #         })
            # self.env['properties.values.variant'].create(list_data)

            if not response1.get('data').get('id'):
                raise exceptions.AccessError(_("Error trying to update product variant in Omna's API."))
            else:
                self.env.user.notify_channel('info', _(
                    'The task to update variant data on marketplace have been created, please go to "System\Tasks" to check out the task status.'),
                                             _("Information"), True)


    def variant_update_ecommerce(self, integration_id, product_template_id, variant_list):
        response1 = response2 = {}
        query1 = []
        for item in variant_list:
            if item.omna_variant_id:
                # new_price = 0
                #
                # if item.product_tmpl_id.taxes_id.price_include:
                #     aux_price = item.product_tmpl_id.omna_tax_id.amount + 100
                #     to_round = item.product_tmpl_id.list_price / (aux_price / 100)
                #     formatted_string = str(truncate(to_round, 6))
                #     new_price = round(to_round, 5) if int(formatted_string[-1]) <= 5 else round(to_round, 6)
                #
                # if not item.product_tmpl_id.taxes_id.price_include:
                #     new_price = item.product_tmpl_id.list_price

                data = {
                    'variant_id': item.omna_variant_id,
                    'sku': item.default_code,
                    # 'price': item.price_extra + new_price,
                    'price': item.price_extra + item.product_tmpl_id.list_price,
                    'package': {'weight': item.peso,
                                'height': item.alto,
                                'length': item.longitud,
                                'width': item.ancho,
                                'content': "No definido"
                                }
                }

                # # POST https://cenit.io/app/ecapi-v1/products/{product_id}/variants/{variant_id}
                # response1 = self.post('products/%s/variants/%s' % (product_template_id.omna_product_id, item.omna_variant_id), {'data': data})

                query1.append(data)

        if query1:
            # POST https://cenit.io/app/ecapi-v1/products/{product_id}/variants/{variant_id}
            response1 = self.put('products/%s/variants' % (product_template_id.omna_product_id,), {'data': query1})

        query2 = []

        for item in variant_list:
            if item.omna_variant_id:
                data2 = {
                    "variant_id": item.omna_variant_id,
                    "properties": [{"id": X.property_name, "value": X.property_stored_value} for X in item.property_ids]
                }

                data2["properties"].append({"id": "price_adjustment", "value": item.price_adjustment})
                data2["properties"].append({"id": "price_adjustment_type", "value": item.price_adjustment_type})
                # data2 = {
                #     "variant_id": item.omna_variant_id,
                #     "properties": [{"id": int(item2.attribute_id.omna_attribute_id),
                #                     "value": int(item2.product_attribute_value_id.omna_attribute_value_id)} for item2 in
                #                    item.product_template_attribute_value_ids]
                # }

                # # POST https://cenit.io/app/ecapi-v1/integrations/{integration_id}/products/{product_id}/variants/{variant_id}
                # response2 = self.post('integrations/%s/products/%s/variants/%s' % (integration_id, product_template_id.omna_product_id, item.omna_variant_id), {"data": data2})

                query2.append(data2)

        if query2:
            # POST https://cenit.io/app/ecapi-v1/integrations/{integration_id}/products/{product_id}/variants/{variant_id}
            response2 = self.post('integrations/%s/products/%s/variants' % (integration_id, product_template_id.omna_product_id,), {"data": query2})

        # if response1 and response2:
        #     if not (response1.get('data') and response1.get('type') == 'variant') or not (response2.get('data') and response2.get('type') == 'di_variant'):
        #         raise exceptions.AccessError(_("Error trying to update product variant in Omna's API."))



class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = ['product.template', 'omna.api']

    @api.model
    def _current_tenant(self):
        current_tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)],
                                                        limit=1)
        if current_tenant:
            return current_tenant.id
        else:
            return None

    taxes_id = fields.Many2many('account.tax', 'product_taxes_rel', 'prod_id', 'tax_id',
                                help="Default taxes used when selling the product.", string='Customer Taxes',
                                domain=['&', '&', ('type_tax_use', '=', 'sale'), ('omna_tax_rule_id', '=', False), ('integration_id', '=', False)],
                                default=lambda self: self.env.company.account_sale_tax_id)
    omna_tenant_id = fields.Many2one('omna.tenant', 'Tenant', default=_current_tenant)
    omna_product_id = fields.Char("Product identifier in OMNA", index=True)
    integration_ids = fields.One2many('omna.integration_product', 'product_template_id', 'Integrations')
    integrations_data = fields.Char('Integrations data')
    simple_product = fields.Boolean('Simple product', default=False)
    integration_linked_ids = fields.Many2many('omna.integration', 'omna_integration_product_template_rel', string='Linked Integrations')
    # category_ids = fields.Many2many('product.category', string='Sale Categories')
    # category_ids = fields.Many2one('product.category', string='Sale Categories')
    peso = fields.Float('Weight (Kg)', digits=(16, 2), default=0)
    alto = fields.Float('Height (Cm)', digits=(16, 2), default=0)
    longitud = fields.Float('Length (Cm)', digits=(16, 2), default=0)
    ancho = fields.Float('Width (Cm)', digits=(16, 2), default=0)
    overwrite = fields.Boolean('Overwrite package information in all variants', default=False)
    omna_tax_id = fields.Many2one('account.tax', string='Omna Tax ID', help="Default taxes used in external ecommerce platform.", domain=[('omna_tax_rule_id', '!=', False), ('integration_id', '!=', False)])
    locking_default_code = fields.Boolean('Overwrite package information in all variants', compute='_locking_default_code', store=True)
    omna_variant_qty = fields.Integer('Omna Variant Qty', default=0)
    property_ids = fields.One2many('properties.values.product', 'product_template_id', 'Properties')


    def _create_variant_ids(self):
        if not self._context.get('internal_variant', False):
            return super(ProductTemplate, self)._create_variant_ids()


    @api.model
    def create(self, vals_list):
        if self.env.context.get('from_omna_api'):
            return super(ProductTemplate, self).create(vals_list)
        else:
            if isinstance(vals_list, list):
                for item in vals_list:
                    if isinstance(item, dict):
                        data = {
                            'name': item.get('name'),
                            'price': item.get('list_price', 0),
                            'description': item.get('description', "No definido"),
                            'package': {'weight': item.get('peso', 0), 'height': item.get('alto', 0), 'length': item.get('longitud', 0),
                                        'width': item.get('ancho', 0), 'content': "No definido"}
                        }

                        response = self.post('products', {'data': data})
                        if response.get('data').get('id'):
                            product = response.get('data')

                            vals_list['omna_product_id'] = response.get('data').get('id')
                            integrations = []
                            aux = []
                            for integration in product.get('integrations'):
                                integrations.append(integration.get('id'))
                                integration_id = self.env['omna.integration'].search([('integration_id', '=', integration.get('id'))])
                                aux.append((0, 0, {'integration_ids': integration_id.id,
                                                   'remote_product_id': integration.get('product').get('remote_product_id'),
                                                   'delete_from_integration': True}))

                            omna_integration = self.env['omna.integration'].search([('integration_id', 'in', integrations)])
                            vals_list['integration_linked_ids'] = [(6, 0, omna_integration.ids)]
                            vals_list['integration_ids'] = aux
                        else:
                            raise exceptions.AccessError(_("Error trying to push product to Omna's API."))
            else:
                data = {
                    'name': vals_list.get('name'),
                    'price': vals_list.get('list_price', 0),
                    'description': vals_list.get('description', "No definido"),
                    'package': {'weight': vals_list.get('peso', 0), 'height': vals_list.get('alto', 0),
                                'length': vals_list.get('longitud', 0),
                                'width': vals_list.get('ancho', 0), 'content': "No definido"}
                }

                response = self.post('products', {'data': data})
                if response.get('data').get('id'):
                    product = response.get('data')

                    vals_list['omna_product_id'] = response.get('data').get('id')
                    integrations = []
                    aux = []
                    for integration in product.get('integrations'):
                        integrations.append(integration.get('id'))
                        integration_id = self.env['omna.integration'].search([('integration_id', '=', integration.get('id'))])
                        aux.append((0, 0, {'integration_ids': integration_id.id,
                                           'remote_product_id': integration.get('product').get('remote_product_id'),
                                           'delete_from_integration': True}))

                    omna_integration = self.env['omna.integration'].search([('integration_id', 'in', integrations)])
                    vals_list['integration_linked_ids'] = [(6, 0, omna_integration.ids)]
                    vals_list['integration_ids'] = aux
                else:
                    raise exceptions.AccessError(_("Error trying to push product to Omna's API."))

            return super(ProductTemplate, self).create(vals_list)


    def write(self, vals):
        if self.env.context.get('from_omna_api'):
            return super(ProductTemplate, self).write(vals)
        else:
            for record in self:
                if "create_product_product" in self._context:
                    vals['name'] = record.name
                data = {
                    'name': vals.get('name', record.name),
                    'price': vals.get('list_price', record.list_price),
                    'description': vals.get('description', record.description),
                    'package': {'weight': vals.get('peso', record.peso), 'height': vals.get('alto', record.alto),
                                'length': vals.get('longitud', record.longitud),
                                'width': vals.get('ancho', record.ancho),
                                'content': "No definido",
                                'overwrite': vals.get('overwrite', record.overwrite)}
                }

                response = self.post('products/%s' % record.omna_product_id, {'data': data})
                if not response.get('data').get('id'):
                    raise exceptions.AccessError(_("Error trying to update products in Omna's API."))

            return super(ProductTemplate, self).write(vals)



    def unlink(self):
        # self.check_access_rights('unlink')
        # self.check_access_rule('unlink')
        # published_list = self.mapped('integration_ids.active_on_sale')
        # linked_list = self.mapped('integration_ids.state')
        #
        # if (True in published_list) or ('linked' in linked_list):
        #     raise UserError("You have to UNLINK and UNPUBLISH this product from all integrations before delete.")
        #
        # to_delete = [X.omna_product_id for X in self if X.type != 'service']
        # integrations = [X.integration_ids.integration_ids.integration_id for X in self if X.type != 'service']
        #
        # if not self._context.get('import_file') and to_delete and integrations:
        #     data = {
        #         "data": {
        #             "product_ids": to_delete,
        #             "integration_ids": integrations,
        #             "delete_from_integration": True
        #         }
        #     }
        #
        #     response1 = self.delete('products/link', data)
        #     record_id = self.env.ref('ecapi_lazada.delete_unlinked_products_cron').id
        #     data = {'active': True, 'nextcall': (datetime.now() + timedelta(minutes=3)).strftime('%Y-%m-%d %H:%M:%S'), 'user_id': self.env.uid}
        #     self.env['ir.cron'].browse(record_id).write(data)

        return super(ProductTemplate, self).unlink()


    def delete_after_unlink(self):
        response = self.sudo().delete('products/all')
        return True


    # def category_tree(self, arr, parent_id, category_id, integration_id, category_obj, list_category):
    #     # integration_id = self.env['omna.integration'].search([('name', '=', integration_category_name)])
    #     if len(arr) == 1:
    #         name = arr[0]
    #         c = category_obj.search(['|', ('omna_category_id', '=', category_id), '&',
    #                                  ('name', '=', name), ('parent_id', '=', parent_id),
    #                                  ('integration_id', '=', integration_id)], limit=1)
    #         if not c:
    #             c = category_obj.create({'name': name, 'omna_category_id': category_id,
    #                                      'parent_id': parent_id,
    #                                      'integration_id': integration_id})
    #
    #         else:
    #             c.write({'name': name, 'parent_id': parent_id})
    #
    #         list_category.append(c.id)
    #         return list_category
    #
    #     elif len(arr) > 1:
    #         name = arr[0]
    #         c = category_obj.search(
    #             [('name', '=', name), ('integration_category_name', '=', integration_id)], limit=1)
    #         if not c:
    #             c = category_obj.create(
    #                 {'name': name, 'parent_id': parent_id, 'integration_category_name': integration_id})
    #
    #         list_category.append(c.id)
    #         self.category_tree(arr[1:], c.id if c else False, category_id, integration_id, category_obj,
    #                            list_category)



    def read(self, fields=None, load='_classic_read'):
        category_id = False
        categ_result = False
        vals = {}

        if (len(self) <= 1) and self.integration_linked_ids and not (self.categ_id):
            response = self.get('integrations/%s/products/%s' % (self.integration_linked_ids.integration_id, self.omna_product_id), {'with_details': True})
            data = response.get('data')
            category_or_brands = data.get('integration').get('product').get('properties', [])
            for cat_br in category_or_brands:
                if (cat_br.get('id') == 'category_id') and (cat_br.get('options')):
                    category_id = cat_br.get('value')

            if category_id:
                categ_result = self.env['product.category'].search([('omna_category_id', '=', category_id)])

            if categ_result:
                vals.update({'categ_id': categ_result.id})

            self.with_context(from_omna_api=True).write(vals)
            self.env.cr.commit()

        return super(ProductTemplate, self).read(fields=fields, load=load)


    @api.depends('product_variant_ids', 'product_variant_ids.default_code')
    def _locking_default_code(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.locking_default_code = False
        for template in (self - unique_variants):
            template.locking_default_code = True


    @api.depends('product_variant_ids', 'product_variant_ids.default_code')
    def _compute_default_code(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.default_code = template.product_variant_ids.default_code
        for template in (self - unique_variants):
            aux_value = template.default_code
            template.default_code = aux_value



class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'omna.api']

    lst_price = fields.Float(compute=False, inverse=False)
    omna_variant_id = fields.Char("Product Variant identifier in OMNA", index=True)
    integration_ids = fields.One2many('omna.integration_variant', 'product_product_id', 'Integrations')
    variant_integrations_data = fields.Char('Integrations data')
    integration_linked_ids = fields.Many2many('omna.integration', 'omna_integration_product_product_rel', string='Linked Integrations')
    # brand_ids = fields.Many2many('product.brand', string='Brand')
    # category_ids = fields.Many2many('product.category', string='Category')
    quantity = fields.Integer('Quantity')
    peso = fields.Float('Weight (Kg)', digits=(16, 2), default=0)
    alto = fields.Float('Height (Cm)', digits=(16, 2), default=0)
    longitud = fields.Float('Length (Cm)', digits=(16, 2), default=0)
    ancho = fields.Float('Width (Cm)', digits=(16, 2), default=0)
    label_full_name = fields.Char('Variant Label Name', compute='_label_full_name')
    custom_description = fields.Text('Description')
    internal_variant = fields.Boolean('Determine if this variant will be published', default=False)
    price_adjustment = fields.Float('Price adjustment', digits=(16, 2), default=0)
    price_adjustment_type = fields.Selection([('none', 'None'),
                                  ('variation', 'Variation'),
                                  ('percent', 'Percent ( % )'),
                                  ('replace', 'Replace')], 'Price adjustment type', default='none')
    property_ids = fields.One2many('properties.values.variant', 'product_product_id', 'Properties')
    omna_variant_id_related = fields.Char(related='product_template_attribute_value_ids.product_attribute_value_id.omna_attribute_value_id', store=True)



    def _label_full_name(self):
        for record in self:
            record.label_full_name = "%s [%s]" % (record.name, record.default_code)


    # TODO Publish variant in OMNA when supported
    # Super importante, hay que agregar el codigo a ejecutar cuando se este importando desde el api de Omna las variantes
    # Es lo correspondiente a esta validación  if self._context.get('omna_import_info'):
    # Para los escenarios de importación implementados en el wizard 'omna.sync_variant_wizard'
    def create(self, vals_list):
        # if self._context.get('omna_import_info'):
        if self.env.context.get('from_omna_api'):
            return super(ProductProduct, self).create(vals_list)

        else:
            product_tmpl_id = vals_list[0].get('product_tmpl_id') if isinstance(vals_list, list) else vals_list.get('product_tmpl_id')
            template_id = self.env['product.template'].search([('id', '=', product_tmpl_id)])

            for item in vals_list:
                if isinstance(item, dict):
                    # if item.get('product_template_attribute_value_ids')[0][2]:
                    if template_id:
                        # rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=len(template_id.default_code)))
                        rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
                        data = {
                            "sku": item.get('default_code', rand_str),
                            "price": item.get('lst_price', template_id.list_price),
                            # "original_price": item.get('standard_price', 0),
                            "package": {
                                "weight": item.get('peso', 0),
                                "height": item.get('alto', 0),
                                "length": item.get('longitud', 0),
                                "width": item.get('ancho', 0),
                                "content": "No definido"
                            }
                        }
                        item['default_code'] = data.get('sku')

                        response = self.post('products/%s/variants' % template_id.omna_product_id, {'data': data})
                        if response.get('data').get('id'):
                            product = response.get('data')
                            item['product_tmpl_id'] = template_id.id
                            item['omna_variant_id'] = product.get('id')
                            # item['contenido'] = template_id.contenido
                            item['peso'] = template_id.peso
                            item['alto'] = template_id.alto
                            item['longitud'] = template_id.longitud
                            item['ancho'] = template_id.ancho
                            # item['custom_description'] = template_id.contenido

                        else:
                            raise exceptions.AccessError("Error trying to push variants to Omna's API.")

            return super(ProductProduct, self).create(vals_list)


    def write(self, vals):
        if self.env.context.get('from_omna_api'):
            return super(ProductProduct, self).write(vals)
        else:
            for record in self:
                if record.omna_variant_id:
                    data = {
                        'price': record.price_extra,
                        'sku': vals.get('default_code', record.default_code),
                        'package': {'weight': vals.get('peso', record.peso),
                                    'height': vals.get('alto', record.alto),
                                    'length': vals.get('longitud', record.longitud),
                                    'width': vals.get('ancho', record.ancho),
                                    'content': "No definido"
                                    }
                    }

                    response = self.post('products/%s/variants/%s' % (record.product_tmpl_id.omna_product_id, record.omna_variant_id), {'data': data})
                    if not response.get('data').get('id'):
                        raise exceptions.AccessError(_("Error trying to update product variant in Omna's API."))

            return super(ProductProduct, self).write(vals)


    def unlink(self):
        # self.check_access_rights('unlink')
        # self.check_access_rule('unlink')
        #
        # omna_products = self.mapped('product_tmpl_id.omna_product_id')
        #
        # if not self._context.get('import_file') and omna_products:
        #     for rec in self:
        #         integrations = rec.mapped('integration_ids.integration_ids.integration_id')
        #         data = {
        #             "integration_ids": integrations,
        #             "delete_from_integration": True,
        #         }
        #
        #         try:
        #             response = rec.delete('products/%s/variants/%s/link' % (rec.product_tmpl_id.omna_product_id, rec.omna_variant_id), {'data': data})
        #         except Exception as e:
        #             _logger.error(e)
        #     record_id = self.env.ref('ecapi_lazada.delete_unlinked_variants_cron').id
        #     data = {'active': True,
        #             'nextcall': (datetime.now() + timedelta(minutes=3)).strftime('%Y-%m-%d %H:%M:%S'),
        #             'user_id': self.env.uid,
        #             'code': "model.delete_after_unlink(%s)" % (str(omna_products))}
        #     self.env['ir.cron'].browse(record_id).write(data)
        return super(ProductProduct, self).unlink()


    def delete_after_unlink(self, omna_product_ids):
        for item in omna_product_ids:
            response = self.delete('products/%s/variants/all' % (item,))


    def launch_config_variant(self):

        """
        <record id="product_attribute_value_action" model="ir.actions.act_window">
            <field name="name">Product Variant Values</field>
            <field name="res_model">product.template.attribute.value</field>
            <field name="view_mode">tree,form</field>
            <field name="domain">[('product_tmpl_id', '=', active_id)]</field>
            <field name="view_ids"
                    eval="[(5, 0, 0),
                    (0, 0, {'view_mode': 'tree', 'view_id': ref('product.product_template_attribute_value_view_tree')}),
                    (0, 0, {'view_mode': 'form', 'view_id': ref('product.product_template_attribute_value_view_form')})]" />
            <field name="context">{
                'default_product_tmpl_id': active_id,
                'search_default_active': 1,
            }</field>
        </record>
        :return:
        """

        context = dict(
            self.env.context,
        )

        context.update({'default_product_tmpl_id': self.product_tmpl_id.id, 'search_default_active': 1})

        action_result = {
            'name': 'Product Variant Values',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'product.template.attribute.value',
            'domain': [('ptav_product_variant_ids', 'in', self.id)],
            'view_ids': [(5, 0, 0),
                    (0, 0, {'view_mode': 'tree', 'view_id': self.env.ref('product.product_template_attribute_value_view_tree').id}),
                    (0, 0, {'view_mode': 'form', 'view_id': self.env.ref('product.product_template_attribute_value_view_form').id})],
            'context': context,
        }

        return action_result



class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'omna.api']

    @api.model
    def _current_tenant(self):
        current_tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)],
                                                        limit=1)
        if current_tenant:
            return current_tenant.id
        else:
            return None

    omna_tenant_id = fields.Many2one('omna.tenant', 'Tenant', default=_current_tenant)
    omna_id = fields.Char("OMNA Order ID", index=True)
    omna_order_reference = fields.Char("OMNA Order Reference", index=True)

    integration_id = fields.Many2one('omna.integration', 'OMNA Integration')
    integration_name = fields.Char(string="OMNA Integration",
                                         related='integration_id.name')
    doc_type = fields.One2many('omna.doc.type', 'sale_order', string='Doc type')
    doc_omna = fields.One2many('omna.sale.doc', 'sale_order_doc', string='Omna doc')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', tracking=4)


    def action_cancel(self):
        # orders = self.filtered(lambda order: not order.origin == 'OMNA')
        # if orders:
        #     orders.write({'state': 'cancel'})
        for order in self.filtered(lambda order: order.origin == 'OMNA'):
            response = self.delete('orders/%s' % order.omna_id)
            # if response:
            #     order.write({'state': 'cancel'})

        return self.write({'state': 'cancel'})

    def action_cancel_from_integration(self):
        for order in self.filtered(lambda x: x.origin == 'OMNA'):
            response = self.delete('integrations/%s/orders/%s' %
                                   (order.integration_id.integration_id, order.omna_order_reference))
            if response:
                # order.action_cancel()
                self.env.user.notify_channel('warning', _(
                    'The task to cancel the order from the integration have been created, please '
                    'go to "System\Tasks" to check out the task status.'),
                                             _("Information"), True)
                order.write({'state': 'cancel'})

    def retrieve_order(self):
        try:
            orders = []
            for order in self:
                # https://cenit.io/app/ecapi-v1/orders/{order_id}
                response = self.get(
                    'orders/%s' % order.omna_id, {})
                data = response.get('data')
                orders.append(data)
                self.env['omna.order.mixin'].sync_orders(orders)


        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)

    @api.depends('order_line.price_unit')
    def _amount_all(self):
        for order in self:
            if not order.omna_id:
                amount_untaxed = amount_tax = 0.0
                for line in order.order_line:
                    amount_untaxed += line.price_subtotal
                    amount_tax += line.price_tax
                order.update({
                    'amount_untaxed': amount_untaxed,
                    'amount_tax': amount_tax,
                    'amount_total': amount_untaxed + amount_tax,
                })


    def action_cancel(self):
        order_list = self.filtered(lambda x: x.origin == 'OMNA')
        for order in order_list:
            response = self.delete('integrations/%s/orders/%s' %
                                   (order.integration_id.integration_id, order.omna_order_reference))
        self.env.user.notify_channel('warning', _(
            'The task to cancel the orders proceed from Prestashop have been created, please '
            'go to "System\Tasks" to check out the task status.'),
                                     _("Information"), True)
        return self.write({'state': 'cancel'})


    def action_view_sale_advance_payment_inv(self):

        context = dict(
            self.env.context,
        )

        # context.update({'default_product_tmpl_id': self.product_tmpl_id.id, 'search_default_active': 1})

        action_result = {
            'name': 'Create invoices',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'sale.advance.payment.inv',
            'binding_view_types': 'list',
            'groups_id': [(4,self.env.ref('sales_team.group_sale_salesman'))],
            'binding_model_id': self.env.ref("sale.model_sale_order"),
            'context': context,
        }

        return action_result



class OmnaOrderLine(models.Model):
    _inherit = 'sale.order.line'

    omna_id = fields.Char("OMNA OrderLine ID", index=True)



class OmnaSaleDoc(models.Model):
    _name = 'omna.sale.doc'
    _inherit = ['omna.api']

    file = fields.Many2many('ir.attachment', string='Files')
    mime_type = fields.Char("text/html")
    title = fields.Char("Title")
    document_type = fields.Many2one('omna.doc.type', string='Type document')
    sale_order_doc = fields.Many2one('sale.order', string='Order')
    omna_doc_id = fields.Char("Document identifier in OMNA", index=True)



class OmnaDocType(models.Model):
    _name = 'omna.doc.type'
    _inherit = ['omna.api']
    _rec_name = "type"

    type = fields.Char("Document type")
    title =fields.Char("Title document type")
    omna_doc_type_id = fields.Char("Document type identifier in OMNA", index=True)
    sale_order = fields.Many2one('sale.order', string='Order')



class OmnaFilters(models.Model):
    _name = 'omna.filters'
    _rec_name = 'title'

    name = fields.Char("Name")
    title = fields.Char("Title")
    type = fields.Char("Type")



class OmnaTask(models.Model):
    _name = 'omna.task'
    _inherit = 'omna.api'
    _rec_name = 'description'

    status = fields.Selection(
        [('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed'),
         ('retrying', 'Retrying')], 'Status',
        required=True)
    description = fields.Text('Description', required=True)
    progress = fields.Float('Progress', required=True)
    task_created_at = fields.Datetime('Created At')
    task_updated_at = fields.Datetime('Updated At')
    task_execution_ids = fields.One2many('omna.task.execution', 'task_id', 'Executions')
    task_notification_ids = fields.One2many('omna.task.notification', 'task_id', 'Notifications')

    def read(self, fields_read=None, load='_classic_read'):
        result = []
        tzinfos = {
            'PST': -8 * 3600,
            'PDT': -7 * 3600,
        }
        for task_id in self.ids:
            task = self.get('tasks/%s' % omna_id2real_id(task_id), {})
            data = task.get('data')
            res = {
                'id': task_id,
                'status': data.get('status'),
                'description': data.get('description'),
                'progress': float(data.get('progress')),
                'task_created_at': fields.Datetime.to_string(
                    dateutil.parser.parse(data.get('created_at'), tzinfos=tzinfos).astimezone(pytz.utc)) if data.get(
                    'created_at') else None,
                'task_updated_at': fields.Datetime.to_string(
                    dateutil.parser.parse(data.get('updated_at'), tzinfos=tzinfos).astimezone(pytz.utc)) if data.get(
                    'updated_at') else None,
                'task_execution_ids': [],
                'task_notification_ids': []
            }
            for execution in data.get('executions', []):
                res['task_execution_ids'].append((0, 0, {
                    'status': execution.get('status'),
                    'exec_started_at': fields.Datetime.to_string(
                        dateutil.parser.parse(execution.get('started_at'), tzinfos=tzinfos).astimezone(
                            pytz.utc)) if execution.get('started_at') else None,
                    'exec_completed_at': fields.Datetime.to_string(
                        dateutil.parser.parse(execution.get('completed_at'), tzinfos=tzinfos).astimezone(
                            pytz.utc)) if execution.get('completed_at') else None,
                }))
            for notification in data.get('notifications', []):
                res['task_notification_ids'].append((0, 0, {
                    'status': notification.get('status'),
                    'message': notification.get('message')
                }))
            result.append(res)

        return result

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        params = {}
        for term in args:
            if term[0] == 'description':
                params['term'] = term[2]
            if term[0] == 'status':
                params['status'] = term[2]

        if count:
            tasks = self.get('tasks', params)
            return int(tasks.get('pagination').get('total'))
        else:
            params['limit'] = limit
            params['offset'] = offset
            tasks = self.get('tasks', params)
            task_ids = self.browse([task.get('id') for task in tasks.get('data')])
            return task_ids.ids

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        self.check_access_rights('read')
        fields = self.check_field_access_rights('read', fields)
        result = []
        tzinfos = {
            'PST': -8 * 3600,
            'PDT': -7 * 3600,
        }
        params = {
            'limit': limit,
            'offset': offset,
        }
        for term in domain:
            if term[0] == 'description':
                params['term'] = term[2]
            if term[0] == 'status':
                params['status'] = term[2]

        tasks = self.get('tasks', params)
        for task in tasks.get('data'):
            res = {
                'id': '1-' + task.get('id'),  # amazing hack needed to open records with virtual ids
                'status': task.get('status'),
                'description': task.get('description'),
                'progress': float(task.get('progress')),
                'task_created_at': odoo.fields.Datetime.to_string(
                    dateutil.parser.parse(task.get('created_at'), tzinfos=tzinfos).astimezone(pytz.utc)),
                'task_updated_at': odoo.fields.Datetime.to_string(
                    dateutil.parser.parse(task.get('updated_at'), tzinfos=tzinfos).astimezone(pytz.utc)),
            }
            result.append(res)

        return result

    def retry(self):
        self.ensure_one()
        response = self.get('/tasks/%s/retry' % omna_id2real_id(self.id))
        return True

    def unlink(self):
        self.check_access_rights('unlink')
        self.check_access_rule('unlink')
        for rec in self:
            response = rec.delete('tasks/%s' % omna_id2real_id(rec.id))
        return True



class OmnaTaskExecution(models.Model):
    _name = 'omna.task.execution'

    status = fields.Selection(
        [('pending', 'Pending'), ('running', 'Running'), ('completed', 'Completed'), ('failed', 'Failed')], 'Status',
        required=True)
    exec_started_at = fields.Datetime('Started At')
    exec_completed_at = fields.Datetime('Completed At')
    task_id = fields.Many2one('omna.task', string='Task')



class OmnaTaskNotification(models.Model):
    _name = 'omna.task.notification'

    type = fields.Selection(
        [('info', 'Info'), ('error', 'Error'), ('warning', 'Warning')], 'Type', required=True)
    message = fields.Char('Message')
    task_id = fields.Many2one('omna.task', string='Task')



class OmnaCollection(models.Model):
    _name = 'omna.collection'
    _inherit = 'omna.api'

    @api.model
    def _current_tenant(self):
        current_tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)],
                                                        limit=1)
        if current_tenant:
            return current_tenant.id
        else:
            return None

    omna_tenant_id = fields.Many2one('omna.tenant', 'Tenant', required=True, default=_current_tenant)
    name = fields.Char('Name', required=True, readonly=True)
    title = fields.Char('Title', required=True, readonly=True)
    omna_id = fields.Char('OMNA Collection id', readonly=True)
    shared_version = fields.Char('Shared Version', readonly=True)
    summary = fields.Text('Summary', readonly=True)
    state = fields.Selection([('not_installed', 'Not Installed'), ('outdated', 'Outdated'), ('installed', 'Installed')],
                             'State', readonly=True)
    updated_at = fields.Datetime('Updated At', readonly=True)
    installed_at = fields.Datetime('Installed At', readonly=True)

    def install_collection(self):
        self.ensure_one()
        self.patch('available/integrations/%s' % self.omna_id, {})
        self.env.user.notify_channel('warning', _(
            'The task to install the collection have been created, please go to "System\Tasks" to check out the task status.'),
                                     _("Information"), True)
        return {'type': 'ir.actions.act_window_close'}

    def uninstall_collection(self):
        self.ensure_one()
        self.delete('available/integrations/%s' % self.omna_id, {})
        self.env.user.notify_channel('warning', _(
            'The task to uninstall the collection have been created, please go to "System\Tasks" to check out the task status.'),
                                     _("Information"), True)
        return {'type': 'ir.actions.act_window_close'}



class OmnaIntegrationChannel(models.Model):
    _name = 'omna.integration_channel'
    _inherit = 'omna.api'

    name = fields.Char('Name', required=True)
    title = fields.Char('Title', required=True)
    group = fields.Char('Group', required=True)
    logo = fields.Char('Logo src', compute='_compute_logo')


    @api.depends('group')
    def _compute_logo(self):
        for record in self:
            record.logo = self._get_logo(record.group)


    @api.model
    def _get_logo(self, group):
        if group == 'Lazada':
            logo = '/ecapi_lazada/static/src/img/lazada_logo.png'
        elif group == 'Qoo10':
            logo = '/ecapi_lazada/static/src/img/qoo10_logo.png'
        elif group == 'Shopee':
            logo = '/ecapi_lazada/static/src/img/shopee_logo.png'
        elif group == 'Shopify':
            logo = '/ecapi_lazada/static/src/img/shopify_logo.png'
        elif group == 'MercadoLibre':
            logo = '/ecapi_lazada/static/src/img/mercadolibre_logo.png'
        elif group == 'Prestashop':
            logo = '/ecapi_lazada/static/src/img/prestashop.png'
        else:
            logo = '/ecapi_lazada/static/src/img/marketplace_placeholder.jpg'
        return logo


    def add_integration(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'omna.integration',
            'view_mode': 'form',
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }



class ProductCategory(models.Model):
    _name = 'product.category'
    _inherit = ['product.category', 'omna.api']

    @api.model
    def _current_tenant(self):
        current_tenant = self.env['omna.tenant'].search([('id', '=', self.env.user.context_omna_current_tenant.id)],
                                                        limit=1)
        if current_tenant:
            return current_tenant.id
        else:
            return None

    omna_tenant_id = fields.Many2one('omna.tenant', 'Tenant', default=_current_tenant)
    omna_category_id = fields.Char("Category identifier in OMNA", index=True)
    integration_id = fields.Many2one('omna.integration', 'OMNA Integration')
    integration_category_name = fields.Char(related='integration_id.name', readonly=False, store=True)



class ProductAttribute(models.Model):
    _name = "product.attribute"
    _inherit = "product.attribute"

    omna_attribute_id = fields.Char("Attribute identifier in OMNA", index=True)



class ProductAttributeValue(models.Model):
    _name = "product.attribute.value"
    _inherit = "product.attribute.value"

    omna_attribute_value_id = fields.Char("Attribute Value identifier in OMNA", index=True)



class Location(models.Model):
    _name = 'stock.location'
    _inherit = ['stock.location', 'omna.api']


    omna_id = fields.Char("OMNA Location ID", index=True)
    integration_id = fields.Many2one('omna.integration', 'OMNA Integration')



class AccountTax(models.Model):
    _name = 'account.tax'
    _inherit = 'account.tax'


    omna_tax_rule_id = fields.Char("OMNA Tax ID", index=True)
    integration_id = fields.Many2one('omna.integration', 'OMNA Integration')



class Warehouse(models.Model):
    _name = 'stock.warehouse'
    _inherit = ['stock.warehouse', 'omna.api']


    omna_id = fields.Char("OMNA Warehouse ID", index=True)
    integration_id = fields.Many2one('omna.integration', 'OMNA Integration')


    def create(self, vals):
        warehouse = super(Warehouse, self).create(vals)
        warehouse.view_location_id.write({'omna_id': warehouse.omna_id, 'integration_id': warehouse.integration_id.id})
        self.env.cr.commit()
        return warehouse



class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'omna.api']


    integration_id = fields.Many2one('omna.integration', 'OMNA Integration')
    omna_id = fields.Char("OMNA Customer Ref.")

