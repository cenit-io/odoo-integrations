#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#

from odoo.http import request
import logging
import requests
import json
import werkzeug

from odoo import models, fields, exceptions, api

_logger = logging.getLogger(__name__)


class OmnaSettings(models.TransientModel):
    _name = 'omna.settings'
    _inherit = 'res.config.settings'

    cenit_url = fields.Char('Ecapi URL', default='https://server.cenit.io/app/ecapi_v1_prod')
    mercado_libre_base_url = fields.Char('Mercado Libre Base URL', default='https://sellercenter.lazada.com.my/')
    # lazada_ws_key = fields.Char('Mercado Libre WS Key')


    ############################################################################
    # Default values getters
    ############################################################################
    @api.model
    def get_values(self):
        res = super(OmnaSettings, self).get_values()
        res.update(
            cenit_url=self.env["ir.config_parameter"].sudo().get_param("ecapi_mercado_libre.cenit_url", default=None),
            lazada_base_url=self.env["ir.config_parameter"].sudo().get_param("ecapi_mercado_libre.mercado_libre_base_url", default=None),
            # lazada_ws_key=self.env["ir.config_parameter"].sudo().get_param("ecapi_mercado_libre.lazada_ws_key", default=None),
        )
        return res

    ############################################################################
    # Values setters
    ############################################################################

    def set_values(self):
        super(OmnaSettings, self).set_values()
        for record in self:
            self.env['ir.config_parameter'].sudo().set_param("ecapi_mercado_libre.cenit_url", record.cenit_url or '')
            self.env['ir.config_parameter'].sudo().set_param("ecapi_mercado_libre.mercado_libre_base_url", record.mercado_libre_base_url or '')
            # self.env['ir.config_parameter'].sudo().set_param("ecapi_mercado_libre.lazada_ws_key", record.lazada_ws_key or '')


class OnmaSignInSettings(models.TransientModel):
    _name = "omna.signin.settings"

    def _default_url(self):
        return self.env['ir.config_parameter'].sudo().get_param("ecapi_mercado_libre.cenit_url", 'https://server.cenit.io/app/ecapi_v1_prod')

    cenit_url = fields.Char('ECAPI BASE URL', default=_default_url)

    def execute(self):
        redirect = self.env['ir.config_parameter'].sudo().get_param('web.base.url') + '/omna/sign_in/'
        self.env['ir.config_parameter'].sudo().set_param("ecapi_mercado_libre.cenit_url", self.cenit_url or 'https://server.cenit.io/app/ecapi_v1_prod')
        return {
            "type": "ir.actions.act_url",
            "url": '%s?%s' % (self.cenit_url + '/sign_in', werkzeug.urls.url_encode({'redirect_uri': redirect})),
            "target": "self",
        }
