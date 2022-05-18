# -*- coding: utf-8 -*-
{
    'name': 'ECAPI Ecommerce Lazada',
    'version': '13.0.20220518',
    'category': 'Sales',
    'summary': 'Integration: Lazada',
    'description': 'Integrate global online marketplaces & web-stores with Odoo. Sync products, inventory and orders from multiple channels',
    'author': 'Cenit IO',
    'website': 'https://web.cenit.io',
    'license': 'OPL-1',
    'support': 'support@cenit.io',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_management', 'board', 'stock', 'purchase'],

    # always loaded
    'data': [
        # security
        'security/omna_security.xml',
        'security/ir.model.access.csv',

        # views
        # 'views/assets.xml',
        'views/parent.xml',
        'views/config.xml',
        'views/data.xml',
        'views/integrations.xml',
        'views/integration_channels.xml',
        'views/webhooks.xml',
        'views/tasks.xml',
        'views/flows.xml',
        'views/tenants.xml',
        'views/collections.xml',
        'views/omna_templates.xml',
        'views/dashboard.xml',
        'views/integration_fields.xml',
        'views/stock_location_inherit_views.xml',
        'views/stock_extra_views.xml',
        'views/product_attribute_inherit_views.xml',
        'views/import_log.xml',
        'views/order_payment_views.xml',
        'views/res_users_view.xml',
        # wizard
        'wizard/omna_sync_products_view.xml',
        'wizard/omna_sync_variant_view.xml',
        'wizard/omna_sync_orders_view.xml',
        'wizard/omna_sync_integrations_view.xml',
        'wizard/omna_sync_workflows_view.xml',
        'wizard/omna_action_start_workflows_view.xml',
        'wizard/omna_action_status_workflows_view.xml',
        'wizard/omna_sync_tenants_view.xml',
        'wizard/omna_sync_collections_view.xml',
        #'wizard/omna_publish_product_view.xml',
        #'wizard/omna_unpublish_product_view.xml',
        'wizard/omna_export_order_view.xml',
	    'wizard/omna_export_orders_from_integration_view.xml',
        'wizard/omna_reimport_order_view.xml',
        'wizard/omna_import_resources_view.xml',
        'wizard/omna_update_product_in_integration.xml',
        'wizard/omna_update_variant_in_integration.xml',
        'wizard/wizard_create_variant.xml',
        'wizard/omna_sync_categories_view.xml',
        # 'wizard/omna_sync_brands_view.xml',
        'wizard/omna_sync_doc_orders_view.xml',
        # 'wizard/properties_list_values_view.xml',
        'wizard/link_variant_wizard_view.xml',
        # 'wizard/properties_list_variant_wizard_view.xml',
        'wizard/omna_sync_channels_view.xml',
        'wizard/omna_external_importer_view.xml',
        'wizard/omna_utilities_view.xml',
        'wizard/omna_extra_import_view.xml',
        'wizard/omna_massive_product_opt.xml',
        'wizard/omna_massive_variant_opt.xml',
        'wizard/wizard_stock_item_mov.xml',


        # initial data
        'data/dow.xml',
        'data/wom.xml',
        'data/moy.xml',
        'data/resource_data.xml',

    ],
    'qweb': [
        'static/src/xml/systray.xml',
        'static/src/xml/dashboard_template.xml',
        'static/src/xml/numeric_step.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'images': ['static/images/banner.png'],
    "installable": True,
    'application': True,
    'auto_install': False,
}
