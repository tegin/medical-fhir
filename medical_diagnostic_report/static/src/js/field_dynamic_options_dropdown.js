/*
 * Copyright 2021 CreuBlanca
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
 */
odoo.define("medical_diagnostic_report.field_dynamic_dropdown", function (require) {
    "use strict";
    /*
       This code allows to add a dynamic dropdown in a selection field inside a table.
       To use it, add a selection_options field in the corresponding model of type char.
       The options will be separated by ";". For example: yes;no
       Finally, add these attributes to the field tag:
            widget="dynamic_selection_diagnostic_report"
            context="{'options': selection_options}"
    */
    var core = require("web.core");
    var AbstractField = require("web.AbstractField");
    var field_registry = require("web.field_registry");

    var _lt = core._lt;

    var FieldDynamicDropdown = AbstractField.extend({
        description: _lt("Dynamic Dropdown"),
        template: "FieldSelection",
        supportedFieldTypes: ["char", "integer"],
        events: _.extend({}, AbstractField.prototype.events, {
            change: "_onChange",
        }),
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this._setValues();
        },

        // --------------------------------------------------------------------------
        // Public
        // --------------------------------------------------------------------------

        /**
         * @override
         * @returns {jQuery}
         */
        getFocusableElement: function () {
            return this.$el.is("select") ? this.$el : $();
        },
        /**
         * @override
         */
        isSet: function () {
            return this.value !== false;
        },
        /**
         * Listen to modifiers updates to hide/show the falsy value in the dropdown
         * according to the required modifier.
         *
         * @override
         */
        updateModifiersValue: function () {
            this._super.apply(this, arguments);
            if (!this.attrs.modifiersValue.invisible && this.mode !== "readonly") {
                this._setValues();
                this._renderEdit();
            }
        },

        // --------------------------------------------------------------------------
        // Private
        // --------------------------------------------------------------------------

        /**
         * @override
         * @private
         */
        _formatValue: function (value) {
            var options = _.extend(
                {},
                this.nodeOptions,
                {data: this.recordData},
                this.formatOptions
            );
            var formattedValue = _.find(this.values, function (option) {
                return option[0] === value;
            });
            if (!formattedValue) {
                return value;
            }
            formattedValue = formattedValue[1];
            if (options && options.escape) {
                formattedValue = _.escape(formattedValue);
            }
            return formattedValue;
        },
        /**
         * @override
         * @private
         */
        _renderEdit: function () {
            this.$el.empty();
            for (var i = 0; i < this.values.length; i++) {
                this.$el.append(
                    $("<option/>", {
                        value: JSON.stringify(this.values[i][0]),
                        text: this.values[i][1],
                    })
                );
            }
            this.$el.val(JSON.stringify(this.value));
        },
        /**
         * @override
         * @private
         */
        _renderReadonly: function () {
            this.$el.empty().text(this._formatValue(this.value));
        },
        /**
         * @override
         */
        _reset: function () {
            this._super.apply(this, arguments);
            this._setValues();
        },
        /**
         * Sets the possible field values.
         *
         * @private
         */
        _setValues: function () {
            var context = this.record.getContext({
                additionalContext: this.attrs.context,
            });
            var options = [];
            _.each(context.options.split(";"), function (v) {
                options.push([v, v]);
            });
            this.values = _.reject(options, function (v) {
                return v[0] === false && v[1] === "";
            });
            if (!this.attrs.modifiersValue || !this.attrs.modifiersValue.required) {
                this.values = [[false, this.attrs.placeholder || ""]].concat(
                    this.values
                );
            }
        },

        // --------------------------------------------------------------------------
        // Handlers
        // --------------------------------------------------------------------------

        /**
         * @private
         */
        _onChange: function () {
            var value = JSON.parse(this.$el.val());
            this._setValue(value.toString());
        },
    });
    field_registry.add("dynamic_selection_diagnostic_report", FieldDynamicDropdown);

    return FieldDynamicDropdown;
});
