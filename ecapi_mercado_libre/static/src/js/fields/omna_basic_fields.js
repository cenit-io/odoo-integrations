odoo.define('omna.basic_fields', function (require) {
"use strict";

var core = require('web.core');
var rpc = require('web.rpc');
var basic_fields = require('web.basic_fields');
var DebouncedField = basic_fields.DebouncedField;
var SummernoteManager = require('web_editor.rte.summernote');
var transcoder = require('web_editor.transcoder');
var qweb = core.qweb;

var FieldOmnaIntegrations = DebouncedField.extend({
    custom_events: _.extend({}, DebouncedField.prototype.custom_events, {
        field_changed: '_onFieldChanged',
    }),
    events: _.extend({}, DebouncedField.prototype.events, {
        'input .omna_integrations_basic_field': '_onInput',
        'change .omna_integrations_basic_field': '_onChange',
        'click .o_delete': '_onDeleteTag',
    }),

    init: function () {
        this._super.apply(this, arguments);
        this.propertiesAttr = 'variant' in this.nodeOptions ? 'variant' : 'product';
        // We need to know if the widget is dirty (i.e. if the user has changed
        // the value, and those changes haven't been acknowledged yet by the
        // environment), to prevent erasing that new value on a reset (e.g.
        // coming by an onchange on another field)
        this.data = JSON.parse(this.value);
        this.integrations = {};
        this.integrationsLabels = {};
        var self = this;
        if(self.data.length){
            $.each(self.data, function(index, integration){
                if(!self.integrations.hasOwnProperty(integration.id)){
                    self.integrations[integration.id] = {};
                    self.integrationsLabels[integration.id] = integration.name;
                }
                if(integration.hasOwnProperty(self.propertiesAttr) && integration[self.propertiesAttr].hasOwnProperty('properties')){
                    $.each(integration[self.propertiesAttr]['properties'], function(index, field){
                        self.integrations[integration.id][field.id] = { id: _.uniqueId('omna-integration-field'), name: field.id, label: field.label, input_type: field.input_type, value: field.value, required: field.required, readonly: field.readonly  };
                        if(field.hasOwnProperty('options')){
                            self.integrations[integration.id][field.id].options = field.options;
                        }
                        if(field.hasOwnProperty('options_service_path')){
                            self.integrations[integration.id][field.id].options_service_path = field.options_service_path;
                        }
                    });
                }
            });
        }
        this.isDirty = false;
        this.lastChangeEvent = undefined;
    },

    start: function () {
        new SummernoteManager(this);
        return this._super.apply(this, arguments);
    },

    /**
     * Returns the first field element.
     *
     * @override
     */
    getFocusableElement: function () {
        return this.$el.find('.omna_integrations_basic_field').first() || $();
    },
    /**
     * Re-renders the widget if it isn't dirty. The widget is dirty if the user
     * changed the value, and that change hasn't been acknowledged yet by the
     * environment. For example, another field with an onchange has been updated
     * and this field is updated before the onchange returns. Two '_setValue'
     * are done (this is sequential), the first one returns and this widget is
     * reset. However, it has pending changes, so we don't re-render.
     *
     * @override
     */
    reset: function (record, event) {
        this._reset(record, event);
        if (!event || event === this.lastChangeEvent) {
            this.isDirty = false;
        }
        if (this.isDirty || (event && event.target === this && event.data.changes[this.name] === this.value)) {
            if (this.attrs.decorations) {
                // if a field is modified, then it could have triggered an onchange
                // which changed some of its decorations. Since we bypass the
                // render function, we need to apply decorations here to make
                // sure they are recomputed.
                this._applyDecorations();
            }
            return $.when();
        } else {
            return this._render();
        }
    },

    updateData: function (field) {
        switch(this.integrations[field.integration][field.id].input_type){
            case 'single_select_with_remote_options':
                this.integrations[field.integration][field.id].value = field.value;
                this.integrations[field.integration][field.id].options = [{name: field.label, id: field.value}];
                break;
            case 'multi_select':
                if(this.integrations[field.integration][field.id].value && this.integrations[field.integration][field.id].value.length){
                    if(field.hasOwnProperty('remove') && field.remove){
                        var selected = this.integrations[field.integration][field.id].value ? this.integrations[field.integration][field.id].value.split(',') : [];
                        var new_selected = $.grep(selected, function(el){
                            return el != field.value;
                        });
                        this.integrations[field.integration][field.id].value = new_selected.join(',');
                    }else{
                        this.integrations[field.integration][field.id].value = this.integrations[field.integration][field.id].value + ',' + field.value;
                    }
                }else{
                    this.integrations[field.integration][field.id].value = field.value;
                }
                break;
            default:
                this.integrations[field.integration][field.id].value = field.value;
                break;
        }

        this.isDirty = true;
    },

    _renderField: function(field, integration){
        var self = this;
        switch(field.input_type){
            case 'single_select':
            case 'category_select_box':
            case 'enum_input':
                if (this.mode !== 'edit'  || field.readonly ){
                    return '<tr>' +
                                '<td class="o_td_label"><label class="o_form_label">' + field.label + '</label></td>'+
                                '<td style="width: 100%;"><span name="type" class="o_field_widget">'+ field.value +'</span></td>'+
                            '</tr>';
                }else{
                    var $tr = $('<tr>');
                    $tr.append('<td class="o_td_label"><label class="o_form_label" for="'+ field.id +'">' + field.label + '</label></td>');
                    var $td = $('<td style="width: 100%;">');
                    var $select = $('<select id="'+ field.id +'" class="o_omna_input o_field_widget omna_integrations_basic_field" data-integration="'+ integration +'" name="'+ field.name +'">');
                    if(field.required){
                        $select.addClass('o_omna_required_modifier');
                    }
                    if(field.hasOwnProperty('options')){
                        $.each(field.options, function(i,val) {
                            if(val === field.value){
                                $select.append('<option selected="1" value="' + val + '">' + val + '</option>');
                            }else{
                                $select.append('<option value="' + val + '">' + val + '</option>');
                            }
                        });
                    }
                    $td.append($select);
                    $tr.append($td);
                    return $tr;
                }
                break;
            case 'single_select_with_remote_options':
                var name = ''
                if (this.mode !== 'edit' || field.readonly){
                    if (field.options.length > 0) {
                        var name = field.options[0].name
                    }else{
                        var name = ''
                    }
                    return '<tr>' +
                               '<td class="o_td_label"><label class="o_form_label">' + field.label + '</label></td>'+
                               '<td style="width: 100%;"><span name="type" class="o_field_widget">'+ name + '</span></td>'+
                           '</tr>';
                }else{
                    if (field.options.length > 0) {
                        var name = field.options[0].name
                    }else{
                        var name = ''
                    }
                    var $tr = $('<tr>');
                    $tr.append('<td class="o_td_label"><label class="o_form_label" for="'+ field.id +'">' + field.label + '</label></td>');
                    var $td = $('<td style="width: 100%;">');
                    var $input = $('<input id="'+ field.id +'" class="o_field_char o_field_widget o_omna_input" data-integration="'+integration+'" name="'+ field.name +'" value="' + name + '" type="text">');
                    if(field.required){
                        $input.addClass('o_omna_required_modifier');
                    }
                    if(field.hasOwnProperty('options_service_path')){
                        $input.autocomplete({
                                    source: function (req, resp) {
                                        rpc.query({
                                             route: '/omna/options/service',
                                             params: {path: field.options_service_path, term: req.term}
                                        }).then(function(results){
                                            var values = _.map(results.data, function (x) {
                                                return {
                                                    label: x.name,
                                                    value: x.id
                                                };
                                            });
                                            resp(values);
                                        });
                                    },
                                    select: function (event, ui) {
                                        // we do not want the select event to trigger any additional
                                        // effect, such as navigating to another field.
                                        event.stopImmediatePropagation();
                                        event.preventDefault();

                                        var item = ui.item;
                                        if (item.value) {
                                            self.updateData({id: $input.attr('name'), label: item.label, value: item.value, integration: $input.data('integration')});
                                            $input.val(item.label);
                                            self._doAction();
                                        }
                                        return false;
                                    },
                                    focus: function (event) {
                                        event.preventDefault(); // don't automatically select values on focus
                                    },
                                    close: function (event) {
                                        // it is necessary to prevent ESC key from propagating to field
                                        // root, to prevent unwanted discard operations.
                                        if (event.which === $.ui.keyCode.ESCAPE) {
                                            event.stopPropagation();
                                        }
                                    },
                                    autoFocus: true,
                                    html: true,
                                    minLength: 0,
                                    delay: 200,
                                });
                                $input.autocomplete("option", "position", { my : "left top", at: "left bottom" });
                    }
                    $input.on('click', function (ev) {
                        if ($input.autocomplete("widget").is(":visible")) {
                            $input.autocomplete("close");
                        } else {
                            $input.autocomplete("search"); // search with the input's content
                        }
                    })
                    $td.append($input);
                    $tr.append($td);
                    return $tr;
                }
                break;
            case 'multi_select':
                if (this.mode !== 'edit' || field.readonly ){
                    var $container = $('<div class="o_field_many2manytags">');
                    var tags = this._renderMultiSelectTags(field.value);
                    $container.append(tags);
                    var $tr = $('<tr>');
                    $tr.append('<td class="o_td_label"><label class="o_form_label">' + field.label + '</label></td>');
                    var $td = $('<td style="width: 100%;">');
                    $td.append($container);
                    $tr.append($td);
                    return $tr;
                }else{
                    var $container = $('<div class="o_field_many2manytags o_omna_input">');
                    var tags = this._renderMultiSelectTags(field.value);
                    $container.append(tags);
                    var $tr = $('<tr>');
                    $tr.append('<td class="o_td_label"><label class="o_form_label" for="'+ field.id +'">' + field.label + '</label></td>');
                    var $td = $('<td style="width: 100%;">');
                    var $input = $('<input id="'+ field.id +'" class="o_field_char o_field_widget o_omna_input" data-integration="'+integration+'" name="'+ field.name +'" type="text">');
                    if(field.required){
                        $input.addClass('o_omna_required_modifier');
                    }
                    var options = this._getOptionsMultiSelect(field);
                    $input.autocomplete({
                        source: options,
                        select: function (event, ui) {
                           // we do not want the select event to trigger any additional
                           // effect, such as navigating to another field.
                           event.stopImmediatePropagation();
                           event.preventDefault();

                           var item = ui.item;
                           if (item.value) {
                               self.updateData({id: $input.attr('name'), value: item.value, integration: $input.data('integration')});
                               $input.val("");
                               $container.find('.badge').remove();
                               var tags = self._renderMultiSelectTags(self.integrations[$input.data('integration')][$input.attr('name')].value);
                               $container.prepend(tags);
                               $input.autocomplete("option", "source", self._getOptionsMultiSelect({value: self.integrations[$input.data('integration')][$input.attr('name')].value, options: field.options}));
                               self._doAction();
                           }
                           return false;
                        },
                        focus: function (event) {
                           event.preventDefault(); // don't automatically select values on focus
                        },
                        close: function (event) {
                           // it is necessary to prevent ESC key from propagating to field
                           // root, to prevent unwanted discard operations.
                           if (event.which === $.ui.keyCode.ESCAPE) {
                               event.stopPropagation();
                           }
                        },
                        autoFocus: true,
                        html: true,
                        minLength: 0,
                        delay: 200,
                    });
                    $input.autocomplete("option", "position", { my : "left top", at: "left bottom" });
                    $input.on('click', function () {
                        if ($input.autocomplete("widget").is(":visible")) {
                            $input.autocomplete("close");
                        } else {
                            $input.autocomplete("search"); // search with the input's content
                        }
                    })
                    $container.append($input);
                    $td.append($container);
                    $tr.append($td);
                    return $tr;
                }
                break;
            case 'rich_text':
                if(this.mode !== 'edit'){
                    var $tr = $('<tr>')
                    var $label = $('<td class="o_td_label"><label class="o_form_label">' + field.label + '</label></td>');
                    var $td = $('<td style="width: 100%;">');
                    var $div = $('<div class="oe_form_field oe_form_field_html_text">');
                    var $iframe = $('<iframe class="o_readonly"/>');
                    $iframe.on('load', function () {
                        var $content = $($iframe.contents()[0]).find("body");
                        $content.html(self._textToHtml(field.value));
                        var height = $content[0] ? $content[0].scrollHeight - 16 : 0;
                        $content.css('height', Math.max(30, Math.min(height, 500)) + 'px');
                    });
                    $div.append($iframe);
                    $td.append($div);
                    $tr.append($label, $td);
                    return $tr;
                }else{
                    var $tr = $('<tr>')
                    var $label = $('<td class="o_td_label"><label class="o_form_label" for="'+ field.id +'">' + field.label + '</label></td>');
                    var $td = $('<td style="width: 100%;">');
                    var $div = $('<div id="'+ field.id +'" class="oe_form_field oe_form_field_html_text" data-integration="'+integration+'" name="'+ field.name +'">');
                    var $textarea = $('<textarea>');
                    $textarea.appendTo($div);
                    $textarea.summernote(this._getSummernoteConfig());
                    var $content = $div.find('.note-editable:first');
                    $content.html(this._textToHtml(field.value));
                    // trigger a mouseup to refresh the editor toolbar
                    var mouseupEvent = $.Event('mouseup', {'setStyleInfoFromEditable': true});
                    $content.trigger(mouseupEvent);
                    transcoder.styleToClass($content);
                    transcoder.imgToFont($content);
                    transcoder.linkImgToAttachmentThumbnail($content);
                    // reset the history (otherwise clicking on undo before editing the
                    // value will empty the editor)
                    var history = $content.data('NoteHistory');
                    if (history) {
                        history.reset();
                    }
                    $td.append($div);
                    $tr.append($label, $td);
                    return $tr;
                }
                break;
            default:
                if (this.mode !== 'edit'){
                    return '<tr>' +
                                '<td class="o_td_label"><label class="o_form_label">' + field.label + '</label></td>'+
                                '<td style="width: 100%;"><span name="type" class="o_field_widget">'+ field.value +'</span></td>'+
                            '</tr>';
                }else{
                    var $tr = $('<tr>')
                    var $label = $('<td class="o_td_label"><label class="o_form_label" for="'+ field.id +'">' + field.label + '</label></td>');
                    var $td = $('<td style="width: 100%;">');
                    var $input = $('<input id="'+ field.id +'" class="o_field_char o_field_widget o_omna_input omna_integrations_basic_field" data-integration="'+integration+'" name="'+ field.name +'" value="' + field.value + '" type="text">')
                    if(field.required){
                        $input.addClass('o_omna_required_modifier');
                    }
                    $td.append($input);
                    $tr.append($label, $td);
                    return $tr;
                }
                break;
        }
    },

     /**
     * @private
     * @param {Object} page
     * @param {string} page_id
     * @returns {jQueryElement}
     */
    _renderTabHeader: function (integration, page_id) {
        var $a = $('<a>', {
            'data-toggle': 'tab',
            disable_anchor: 'true',
            href: '#' + page_id,
            class: 'nav-link',
            role: 'tab',
            text: this.integrationsLabels[integration],
        });
        return $('<li>', {class: 'nav-item'}).append($a);
    },
    /**
     * @private
     * @param {Object} page
     * @param {string} page_id
     * @returns {jQueryElement}
     */
    _renderTabPage: function (integration, page_id) {
        var self = this;
        var $result = $('<div class="tab-pane" id="' + page_id + '">');
        var $group = $('<div class="o_group">');
        var $table = $('<table class="o_group o_inner_group o_group_col_6">')
        var $table_body = $table.append('<tbody>')
        var $second_table = $('<table class="o_group o_inner_group o_group_col_6">')
        var $second_table_body = $second_table.append('<tbody>')
        var $rich_text_table = $('<table class="o_group o_inner_group o_group_col_12">')
        var $rich_text_table_body = $rich_text_table.append('<tbody>')
        if(Object.keys(self.integrations[integration]).length){
            var cant = Object.keys(self.integrations[integration]).length;
            var main_prop = [];
            var rich_text_prop = [];
            $.each(self.integrations[integration], function(field){
                if(self.integrations[integration][field].input_type === 'rich_text'){
                    rich_text_prop.push(self.integrations[integration][field]);
                }else{
                    main_prop.push(self.integrations[integration][field]);
                }
            });
            $.each(main_prop, function(index, field){
                if (index % 2 === 0){
                    $table_body.append(self._renderField(field, integration))
                }else{
                    $second_table_body.append(self._renderField(field, integration))
                }
            });
            $.each(rich_text_prop, function(index, field){
                $rich_text_table_body.append(self._renderField(field, integration))
            });
        }
        $group.append($table, $second_table, $rich_text_table);
        $result.append($group);
        return $result;
    },

    _renderMultiSelectTags: function(value){
        var elements = [];
        if (value.length > 0) {
            var selected = value ? value.split(',') : [];
        }else{
            var selected = [];
        }
        $.each(selected, function(index, element){
           elements.push({id: element, display_name: element});
        });
        var tags = qweb.render('FieldMany2ManyTag', {
           elements: elements,
           hasDropdown: false,
           readonly: this.mode === "readonly",
        });
        return tags;
    },

    _prepareHtml: function () {
        var self = this;
        var $headers = $('<ul class="nav nav-tabs" role="tablist">');
        var $pages = $('<div class="tab-content">');
        var autofocusTab = -1;
        // renderedTabs is used to aggregate the generated $headers and $pages
        // alongside their node, so that their modifiers can be registered once
        // all tabs have been rendered, to ensure that the first visible tab
        // is correctly activated
        var renderedTabs = [];
        $.each(this.integrations, function (integration) {
            var pageID = _.uniqueId('omna_integrations_properties_');
            var $header = self._renderTabHeader(integration, pageID);
            var $page = self._renderTabPage(integration, pageID);
            $headers.append($header);
            $pages.append($page);
            renderedTabs.push({
                $header: $header,
                $page: $page,
                node: integration,
            });
        });
        if (renderedTabs.length) {
            var tabToFocus = renderedTabs[Math.max(0, autofocusTab)];
            tabToFocus.$header.find('.nav-link').addClass('active');
            tabToFocus.$page.addClass('active');
        }

        var $integrations_field = $('<div class="o_notebook o_omna_integrations">').append($headers, $pages);
        return $integrations_field;
    },

    _textToHtml: function (text) {
        var value = text || "";
        try {
            $(text)[0].innerHTML; // crashes if text isn't html
        } catch (e) {
            if (value.match(/^\s*$/)) {
                value = '<p><br/></p>';
            } else {
                value = "<p>" + value.split(/<br\/?>/).join("<br/></p><p>") + "</p>";
                value = value
                            .replace(/<p><\/p>/g, '')
                            .replace('<p><p>', '<p>')
                            .replace('<p><p ', '<p ')
                            .replace('</p></p>', '</p>');
            }
        }
        return value;
    },

    _getSummernoteConfig: function () {
        var summernoteConfig = {
            model: this.model,
            id: this.res_id,
            focus: false,
            height: 180,
            toolbar: [
                ['style', ['style']],
                ['font', ['bold', 'italic', 'underline', 'clear']],
                ['fontsize', ['fontsize']],
                ['color', ['color']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['insert', ['link']],
                ['history', ['undo', 'redo']]
            ],
            prettifyHtml: false,
            styleWithSpan: false,
            inlinemedia: ['p'],
            lang: "odoo",
            onChange: this._onChangeSummernote.bind(this),
            disableDragAndDrop: true,
        };

        return summernoteConfig;
    },

    _getOptionsMultiSelect: function(field){
         if (field.value.length > 0) {
            var selected = field.value ? field.value.split(',') : [];
        }else{
            var selected = [];
        }
        var diff = [];
        $.each(field.options, function(index, el){
            if($.inArray(el, selected) == -1){
                diff.push(el);
            }
        });
        return diff;
    },

    _onDeleteTag: function (event) {
        event.preventDefault();
        event.stopPropagation();
        var value = $(event.target).parent().data('id');
        var $input = $(event.target).parent().siblings('input');
        this.updateData({id: $input.attr('name'), value: value, label: value, integration: $input.data('integration'), input_type: $input.data('input_type'), remove: true});
        $input.autocomplete("option", "source", this._getOptionsMultiSelect({value: this.integrations[$input.data('integration')][$input.attr('name')].value, options: this.integrations[$input.data('integration')][$input.attr('name')].options}));
        $(event.target).parent().remove();
        this._doAction();
    },

    isValid: function () {
        var self = this;
        this._isValid = true;
        $.each(self.integrations, function(integration){
            $.each(self.integrations[integration], function(field){
                var $field = self.$el.find('#' + self.integrations[integration][field].id);
                var $label = self.$el.find('label[for=' + self.integrations[integration][field].id + ']');
                if(self.integrations[integration][field].required && !self.integrations[integration][field].value){
                   self._isValid = false;
                   if($field.length){
                        $field.addClass('o_omna_field_invalid');
                   }
                   if($label.length){
                        $label.addClass('o_omna_field_invalid');
                   }
                }else{
                   if($field.length){
                        $field.removeClass('o_omna_field_invalid');
                   }
                   if($label.length){
                        $label.removeClass('o_omna_field_invalid');
                   }
                }
            });
        });
        return self._isValid;
    },

    /**
     * @override
     * @returns {string} the json representation of the properties values
     */
    _getValue: function () {
        for(var i = 0; i < this.data.length; i++){
            for(var j = 0; j < this.data[i][this.propertiesAttr].properties.length; j++){
                if(this.integrations.hasOwnProperty(this.data[i].id) && this.integrations[this.data[i].id].hasOwnProperty(this.data[i][this.propertiesAttr].properties[j].id)){
                    this.data[i][this.propertiesAttr].properties[j].value = this.integrations[this.data[i].id][this.data[i][this.propertiesAttr].properties[j].id].value;
                     if(this.data[i][this.propertiesAttr].properties[j].input_type === 'single_select_with_remote_options'){
                        this.data[i][this.propertiesAttr].properties[j].options = this.integrations[this.data[i].id][this.data[i][this.propertiesAttr].properties[j].id].options
                    }
                }
            }
        }
        return JSON.stringify(this.data);
    },

    _render: function () {
        if (this.attrs.decorations) {
            this._applyDecorations();
        }
        this.$el.empty();
        this.$el.append(this._prepareHtml());
    },

    /**
     * We immediately notify the outside world when this field confirms its
     * changes.
     *
     * @private
     */
    _onChange: function () {
        this._doAction();
    },
    /**
     * Listens to events 'field_changed' to keep track of the last event that
     * has been trigerred. This allows to detect that all changes have been
     * acknowledged by the environment.
     *
     * @param {OdooEvent} event 'field_changed' event
     */
    _onFieldChanged: function (event) {
        this.lastChangeEvent = event;
    },

    _onChangeSummernote: function($content, $editable){
        var $field = $editable.closest('div.oe_form_field');
        transcoder.attachmentThumbnailToLinkImg($editable);
        transcoder.fontToImg($editable);
        transcoder.classToStyle($editable);
        this.updateData({id: $field.attr('name'), value: $editable.html(), label: '', integration: $field.data('integration'), input_type: $field.data('input_type')});
        this._doDebouncedAction();
    },

    _onInput: function (event) {
        var $input = $(event.target);
        this.updateData({id: $input.attr('name'), value: $input.val(), label: $input.val(), integration: $input.data('integration'), input_type: $input.data('input_type')});
        this._doDebouncedAction();
    },
});

return {
    FieldOmnaIntegrations: FieldOmnaIntegrations
}

});