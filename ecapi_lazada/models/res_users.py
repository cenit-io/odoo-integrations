# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _, exceptions
import logging


_logger = logging.getLogger(__name__)

DEFAULT_MESSAGE = "Default message"


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _compute_omna_manager(self):
        self.context_omna_manager = self.has_group('ecapi_lazada.group_omna_manager')

    def _default_current_tenant(self):
        return self.env['omna.tenant'].search([], limit=1).id

    def _default_omna_urls(self):
        url = self.env["ir.config_parameter"].sudo().get_param("ecapi_lazada.cenit_url")
        self.context_omna_get_access_token_url = '%s/%s' % (url, 'get_access_token') if url else None
        self.context_omna_base_url = url if url else None

    @api.depends("create_date")
    def _compute_channel_names(self):
        for record in self:
            res_id = record.id
            record.notify_success_channel_name = "notify_success_%s" % res_id
            record.notify_danger_channel_name = "notify_danger_%s" % res_id
            record.notify_warning_channel_name = "notify_warning_%s" % res_id
            record.notify_info_channel_name = "notify_info_%s" % res_id
            record.notify_default_channel_name = "notify_default_%s" % res_id

    notify_success_channel_name = fields.Char(compute="_compute_channel_names")
    notify_danger_channel_name = fields.Char(compute="_compute_channel_names")
    notify_warning_channel_name = fields.Char(compute="_compute_channel_names")
    notify_info_channel_name = fields.Char(compute="_compute_channel_names")
    notify_default_channel_name = fields.Char(compute="_compute_channel_names")
    context_omna_current_tenant = fields.Many2one('omna.tenant', string='Omna Current Tenant', default=_default_current_tenant)
    context_omna_manager = fields.Boolean('Omna Manager', compute='_compute_omna_manager')
    context_omna_get_access_token_code = fields.Char('Code to retrieve access token from Omna')
    context_omna_get_access_token_url = fields.Char('Url to retrieve access token from Omna', compute='_default_omna_urls')
    context_omna_base_url = fields.Char('Omna API base url', compute='_default_omna_urls')

    def notify_channel(
        self,
        type_message='default',
        message=DEFAULT_MESSAGE,
        title=None,
        sticky=False,
    ):
        # pylint: disable=protected-access
        if not self.env.user._is_admin() and any(
            user.id != self.env.uid for user in self
        ):
            raise exceptions.UserError(
                _("Sending a notification to another user is forbidden.")
            )
        channel_name_field = "notify_{}_channel_name".format(type_message)
        bus_message = {
            "type": type_message,
            "message": message,
            "title": title,
            "sticky": sticky,
        }
        notifications = [
            (record[channel_name_field], bus_message) for record in self
        ]
        self.env["bus.bus"].sendmany(notifications)
