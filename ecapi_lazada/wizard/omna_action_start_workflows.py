# -*- coding: utf-8 -*-

import logging
from odoo import models, api, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class OmnaSyncWorkflows(models.TransientModel):
    _name = 'omna.action_start_workflows_wizard'
    _inherit = 'omna.api'

    def start(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for flow in self.env['omna.flow'].browse(active_ids):
            self.get('flows/%s/start' % flow.omna_id, {})
        return {'type': 'ir.actions.act_window_close'}



