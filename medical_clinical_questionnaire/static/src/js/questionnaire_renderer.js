odoo.define('medical.QuestionnaireRenderer', function (require) {
    "use strict";

    var BasicRenderer = require('web.BasicRenderer');
    var field_registry = require('web.field_registry');
    var fieldUtils = require('web.field_utils');
    var core = require('web.core');
    var qweb = core.qweb;

    var QuestionnaireRenderer = BasicRenderer.extend({
        init: function (parent, state, params) {
            if (params === undefined) {
                params = {};
            }
            if (params.viewType === undefined ) {
                params.viewType = 'questionnaire';
            }
            this._super(parent, state, params);
            if (
                parent !== undefined &&
                parent.mode === 'edit' &&
                params.mode === undefined
            ) {
                this.mode = 'edit';
            }
            this.recordWidgets = {};
        },
        _itemType2Object: function (type) {
            switch (type) {
            case 'string':
                return 'html';
            case 'selection':
                return 'radio';
            default:
                return type;
            }
        },
        _renderView: function () {
            var self = this;
            var $table = $(qweb.render('medical_clinical_questionnaire.table'));
            var $body = $table.find('tbody');
            this.$el.empty();
            $table.appendTo(this.$el);
            var fieldInfo = {}
            _.each(this.state.data, function (data) {
                var field_name = "result_" + data.res_id;
                data.data['field_name'] = field_name;
                var field_type = self._itemType2Object(
                    data.data.question_type);
                data.data['field_type'] = field_type;
                if (
                    data.data[field_name] === undefined &&
                    field_type !== undefined
                ) {
                    var value = data.data.result;
                    data.fields[field_name] = {
                        type: field_type,
                    };
                    if (field_type === 'radio') {
                        var selection = [];
                        _.each(
                            data.data.selection_options.split(';'),
                            function (item) {
                                selection.push([item, item]);
                            }
                        );
                        data.fields[field_name].type = 'selection';
                        data.fields[field_name].selection = selection;
                    }
                    if (
                        field_type === 'date' || field_type === 'datetime'
                    ) {
                        value = fieldUtils.parse[field_type](
                            value, data.fields[field_name], {isUTC: true});
                    }
                    data.data[field_name] = value;
                }
                if (data.data.technical_name) {
                    var response = data.data.questionnaire_id.res_id;
                    if (fieldInfo[response] === undefined) {
                        fieldInfo[response] = {};
                    }
                    fieldInfo[response][data.data.technical_name] = data.data[
                        field_name];
                }
            });
            _.each(this.state.data, function (data) {
                var element = $(qweb.render(
                    'medical_clinical_questionnaire.item',
                    {
                        widget: self,
                        data: data,
                    }
                ));
                var Widget = field_registry.get(data.data.field_type);
                if (Widget !== undefined) {

                    var response = data.data.questionnaire_id.res_id;
                    if (data.data.invisible_condition) {
                        if (py.eval(
                            data.data.invisible_condition, fieldInfo[response]
                        )) {
                            return;
                        }
                    }
                    else if (data.data.is_invisible) {
                        return;
                    }
                    var options = {};
                    var mode = self.mode;
                    if (data.data.options !== undefined && data.data.options) {
                        options = JSON.parse(data.data.options);
                    }
                    if (data.data.readonly_condition) {
                        if (mode === "edit" && py.eval(
                            data.data.readonly_condition, fieldInfo[response])
                        ) {
                            mode = "readonly";
                        }
                    }
                    else if (data.data.readonly) {
                        mode = "readonly";
                    }
                    var widget = new Widget(
                        self, data.data.field_name, data, _.extend({
                            mode: mode,
                        }, options));
                    self.recordWidgets[data.id] = widget;
                    var node = element.find(".result_data");
                    widget.appendTo(node);
                }
                element.appendTo($body);
            });
            return this._super();
        },
    });

    return QuestionnaireRenderer;
});
