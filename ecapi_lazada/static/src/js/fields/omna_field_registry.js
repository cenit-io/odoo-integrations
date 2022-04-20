odoo.define('omna.field_registry', function(require) {
"use strict";

var omna_basic_fields = require('omna.basic_fields');
var integrations_field = omna_basic_fields.FieldOmnaIntegrations;
var registry = require('web.field_registry');

registry
    .add('omna_integrations', integrations_field);

});
