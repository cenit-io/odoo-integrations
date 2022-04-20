odoo.define('omna.systray.TenantMenu', function (require) {
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
    var session = require('web.session');

    var TenantMenu = Widget.extend({
        name: 'tenant_menu',
        template: 'omna.systray.TenantMenu',
        events: {
            'click .o_tenant_button': '_onClickFilterButton',
        },
        /**
         * @override
         */
        start: function () {
            this._$tenants = this.$('.o_omna_systray_dropdown_items');
            var that = this;
            rpc.query({
                model: 'omna.tenant',
                method: 'search_read',
                fields: ['id', 'name', 'current'],
                args: []
            }).then(function (tenants) {
                if (tenants) {
                    that._$tenants.html(QWeb.render('omna.systray.TenantMenuItems', {
                        tenants: tenants,
                        current_tenant: session.user_context.omna_current_tenant
                    }));
                }
            });
            return this._super.apply(this, arguments);
        },
        _onClickFilterButton: function (ev) {
            var that = this;
            rpc.query({
                model: 'omna.tenant',
                method: 'switch_action',
                args: [$(ev.currentTarget).data('tenant')]
            }).then(function (response) {
                if(response){
                    that.do_action('reload_context')
                }
            });
        }
    });
    if(session.user_context.omna_manager){
        SystrayMenu.Items.splice(0, 0, TenantMenu);
    }

    return TenantMenu;

});
