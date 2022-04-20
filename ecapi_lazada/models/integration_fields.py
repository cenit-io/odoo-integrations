# -*- coding: utf-8 -*-

import odoo
import datetime
from odoo import models, fields, api, exceptions, tools, _
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

_logger = logging.getLogger(__name__)


class PropertiesValuesOptionsProduct(models.Model):
    _name = 'properties.values.options.product'
    _inherit = 'omna.api'
    _rec_name = 'option_label'


    property_value_product_id = fields.Many2one('properties.values.product', string='Property', ondelete='cascade')
    option_value = fields.Char(string='Value', required=True)
    option_label = fields.Char(string='Label', required=True)
    property_name = fields.Char(related='property_value_product_id.property_name', store=True)



class PropertiesValuesProduct(models.Model):
    _name = 'properties.values.product'
    _inherit = 'omna.api'
    # _rec_name = 'topic'



    property_name = fields.Char('Property Name', required=True)
    property_type = fields.Char('Property Type', required=True, default='string')
    integration_id = fields.Many2one('omna.integration', 'Integration', required=True, ondelete='cascade')
    property_label = fields.Char('Property Label', required=True)
    property_required = fields.Boolean('Required Property')
    property_readonly = fields.Boolean('ReadOnly Property')
    property_options = fields.Char('Property Options')
    value_option_ids = fields.One2many('properties.values.options.product', 'property_value_product_id', 'Values X Property')
    # ------------------------------------------------------------------------------------------------------------------
    product_template_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade')
    property_value = fields.Char(string='Char Value')
    property_integer_value = fields.Integer(string='Integer Value')
    property_float_value = fields.Float(string='Float Value')
    property_boolean_value = fields.Boolean(string='Boolean Value')
    property_date_value = fields.Date(string='Date Value')
    # property_selection_value = fields.Selection(selection=_get_property_selection_value, string='Selection Value')
    # property_selection_value = fields.Many2one('properties.values.options.product', string='Selection Value', domain="[('property_id', '=', property_id)]")
    property_selection_value = fields.Many2one('properties.values.options.product', string='Selection Value', domain="[('property_name', '=', property_name), ('property_value_product_id', '=', id)]")
    property_rich_text_value = fields.Text(string='Rich Text Value')
    property_multi_selection_value = fields.Many2many('properties.values.options.product', 'multi_select_value_rel', 'property_value_id', 'option_value_id', string='Multi Selection Value')
    property_display_value = fields.Char(string='Assigned Value', compute='_property_display_value')
    property_stored_value = fields.Char(string='Stored Value', compute='_property_display_value')


    # @api.depends('property_value', 'property_integer_value', 'property_float_value', 'property_boolean_value', 'property_date_value',
    #              'property_selection_value', 'property_rich_text_value', 'property_multi_selection_value')
    def _property_display_value(self):
        for record in self:
            flag = False
            if record.property_value:
                record.property_display_value = record.property_value
                record.property_stored_value = record.property_value
                flag = True
            if record.property_integer_value:
                record.property_display_value = record.property_integer_value
                record.property_stored_value = record.property_integer_value
                flag = True
            if record.property_float_value:
                record.property_display_value = record.property_float_value
                record.property_stored_value = record.property_float_value
                flag = True
            if record.property_type == 'boolean':
                record.property_display_value = 'Yes' if record.property_boolean_value else 'No'
                record.property_stored_value = record.property_boolean_value
                flag = True
            if record.property_date_value:
                record.property_display_value = record.property_date_value
                record.property_stored_value = record.property_date_value
                flag = True
            if record.property_selection_value:
                record.property_display_value = record.property_selection_value.option_label
                record.property_stored_value = record.property_selection_value.option_value
                flag = True
            if record.property_rich_text_value:
                record.property_display_value = record.property_rich_text_value
                record.property_stored_value = record.property_rich_text_value
                flag = True
            if record.property_multi_selection_value:
                record.property_display_value = ', '.join([x.option_label for x in record.property_multi_selection_value])
                record.property_stored_value = ', '.join([x.option_value for x in record.property_multi_selection_value])
                flag = True
            if not flag:
                record.property_display_value = ""
                record.property_stored_value = ""



# ----------------------------------------------------------------------------------------------------------------------


class PropertiesValuesOptionsVariant(models.Model):
    _name = 'properties.values.options.variant'
    _inherit = 'omna.api'
    _rec_name = 'option_label'


    property_value_variant_id = fields.Many2one('properties.values.variant', string='Property', ondelete='cascade')
    option_value = fields.Char(string='Value', required=True)
    option_label = fields.Char(string='Label', required=True)
    property_name = fields.Char(related='property_value_variant_id.property_name', store=True)


class PropertiesValuesVariant(models.Model):
    _name = 'properties.values.variant'
    _inherit = 'omna.api'
    # _rec_name = 'topic'



    property_name = fields.Char('Property Name', required=True)
    property_type = fields.Char('Property Type', required=True, default='string')
    integration_id = fields.Many2one('omna.integration', 'Integration', required=True, ondelete='cascade')
    property_label = fields.Char('Property Label', required=True)
    property_required = fields.Boolean('Required Property')
    property_readonly = fields.Boolean('ReadOnly Property')
    property_options = fields.Char('Property Options')
    value_option_ids = fields.One2many('properties.values.options.variant', 'property_value_variant_id', 'Values X Property')
    # ------------------------------------------------------------------------------------------------------------------
    product_product_id = fields.Many2one('product.product', string='Product Variant', required=True, ondelete='cascade')
    property_value = fields.Char(string='Value')
    property_integer_value = fields.Integer(string='Integer Value')
    property_float_value = fields.Float(string='Float Value')
    property_boolean_value = fields.Boolean(string='Boolean Value')
    property_date_value = fields.Date(string='Date Value')
    # property_selection_value = fields.Selection(selection=_get_property_selection_value, string='Selection Value')
    # property_selection_value = fields.Many2one('properties.values.options', string='Selection Value', domain="[('property_id', '=', property_id)]")
    property_selection_value = fields.Many2one('properties.values.options.variant', string='Selection Value', domain="[('property_name', '=', property_name), ('property_value_variant_id', '=', id)]")
    property_rich_text_value = fields.Text(string='Rich Text Value')
    property_multi_selection_value = fields.Many2many('properties.values.options.variant', 'multi_select_value_variant_rel', 'property_value_id', 'option_value_id', string='Multi Selection Value')
    property_display_value = fields.Char(string='Assigned Value', compute='_property_display_value')
    property_stored_value = fields.Char(string='Stored Value', compute='_property_display_value')

    # @api.depends('property_value', 'property_integer_value', 'property_float_value', 'property_boolean_value',
    #              'property_date_value', 'property_selection_value', 'property_rich_text_value',
    #              'property_multi_selection_value')
    def _property_display_value(self):
        for record in self:
            flag = False
            if record.property_value:
                record.property_display_value = record.property_value
                record.property_stored_value = record.property_value
                flag = True
            if record.property_integer_value:
                record.property_display_value = record.property_integer_value
                record.property_stored_value = record.property_integer_value
                flag = True
            if record.property_float_value:
                record.property_display_value = record.property_float_value
                record.property_stored_value = record.property_float_value
                flag = True
            if record.property_type == 'boolean':
                record.property_display_value = 'Yes' if record.property_boolean_value else 'No'
                record.property_stored_value = record.property_boolean_value
                flag = True
            if record.property_date_value:
                record.property_display_value = record.property_date_value
                record.property_stored_value = record.property_date_value
                flag = True
            if record.property_selection_value:
                record.property_display_value = record.property_selection_value.option_label
                record.property_stored_value = record.property_selection_value.option_value
                flag = True
            if record.property_rich_text_value:
                record.property_display_value = record.property_rich_text_value
                record.property_stored_value = record.property_rich_text_value
                flag = True
            if record.property_multi_selection_value:
                record.property_display_value = ', '.join([x.option_label for x in record.property_multi_selection_value])
                record.property_stored_value = ', '.join([x.option_value for x in record.property_multi_selection_value])
                flag = True
            if not flag:
                record.property_display_value = ""
                record.property_stored_value = ""
