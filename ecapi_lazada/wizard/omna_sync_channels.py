# -*- coding: utf-8 -*-

import requests
import base64
import json
import logging
import hmac
import hashlib
from datetime import datetime, timezone, time
from odoo import models, api, exceptions


_logger = logging.getLogger(__name__)


class OmnaSyncChannels(models.TransientModel):
    _name = 'omna.sync_channels_wizard'
    _inherit = 'omna.api'

    def sync_channels(self):
        try:

            result = []
            channels = self.get('available/integrations/channels', {})
            for channel in list(filter(lambda d: d['group'] == 'Lazada', channels.get('data'))):
                res = {
                    # 'id': '1-' + channel.get('name'),
                    'name': channel.get('name'),
                    'title': channel.get('title'),
                    'group': channel.get('group'),
                    # 'logo': self._get_logo(channel.get('group'))
                }
                result.append(res)


            channel_obj = self.env['omna.integration_channel']
            for item in result:
                act_channel = channel_obj.search(['&', '&', ('name', '=', item.get('name')), ('title', '=', item.get('title')), ('group', '=', item.get('group'))])
                if act_channel:
                    act_channel.with_context(synchronizing=True).write(item)
                else:
                    act_channel = channel_obj.with_context(synchronizing=True).create(item)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }
        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)


