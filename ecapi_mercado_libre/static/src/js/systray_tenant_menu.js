/** @odoo-module **/

import SystrayMenu from 'web.SystrayMenu';
import Widget from 'web.Widget';

const { Component } = owl;

var TenantMenu = Widget.extend({
    template: 'ecapi_systray_item.tenant_icon',
    events: {
        'click .tenant_icon': 'onclick_tenant_icon',
    },
    onclick_tenant_icon: function() {
        var self = this;
        self.do_action({
            name: 'Set active tenant',
            res_model: 'activate.tenant.wizard',
            views: [[false, 'form']],
            type: 'ir.actions.act_window',
            view_mode: 'form',
            target: 'new',
            context: { dialog_size: 'small' }
        });
    },
});

SystrayMenu.Items.push(TenantMenu);

export default TenantMenu;

