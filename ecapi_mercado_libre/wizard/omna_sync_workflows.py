# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timezone
from dateutil.parser import parse
from odoo import models, api, exceptions

_logger = logging.getLogger(__name__)


class OmnaSyncWorkflows(models.TransientModel):
    _name = 'omna.sync_workflows_wizard'
    _inherit = 'omna.api'

    def sync_workflows(self):
        try:
            limit = 25
            offset = 0
            requester = True
            flows = []
            while requester:
                response = self.get('flows', {'limit': limit, 'offset': offset})
                data = response.get('data')
                flows.extend(data)
                if len(data) < limit:
                    requester = False
                else:
                    offset += limit

            for flow in flows:
                act_flow = self.env['omna.flow'].search([('omna_id', '=', flow.get('id'))])
                integration = self.env['omna.integration'].search(
                    [('integration_id', '=', flow.get('integration').get('id'))])
                flow_data = {
                    'integration_id': integration.id,
                    'type': flow.get('type'),
                    'omna_id': flow.get('id')
                }
                if type(flow.get('task')) is dict:
                    days_of_week = self.env['omna.filters'].search(
                        [('type', '=', 'dow'), ('name', 'in', flow.get('task').get('scheduler').get('days_of_week'))])
                    weeks_of_month = self.env['omna.filters'].search(
                        [('type', '=', 'wom'), ('name', 'in', flow.get('task').get('scheduler').get('weeks_of_month'))])
                    months_of_year = self.env['omna.filters'].search(
                        [('type', '=', 'moy'), ('name', 'in', flow.get('task').get('scheduler').get('months_of_year'))])
                    start_date = parse('%s %s' % (
                    flow.get('task').get('scheduler').get('start_date'), flow.get('task').get('scheduler').get('time')))
                    flow_data.update({
                        'start_date': start_date,
                        'end_date': parse(flow.get('task').get('scheduler').get('end_date')),
                        'days_of_week': days_of_week,
                        'weeks_of_month': weeks_of_month,
                        'months_of_year': months_of_year,
                    })
                if act_flow:
                    act_flow.with_context(synchronizing=True).write(flow_data)
                else:
                    act_flow = self.env['omna.flow'].with_context(synchronizing=True).create(flow_data)

            return {
                'type': 'ir.actions.client',
                'tag': 'reload'
            }

        except Exception as e:
            _logger.error(e)
            raise exceptions.AccessError(e)
