odoo.define("web.web_widget_warning_dropdown", function(require) {
    "use strict";

    var field_registry = require("web.field_registry");
    var core = require("web.core");
    var qweb = core.qweb;
    var AbstractField = require("web.AbstractField");
    var WarningDropdown = AbstractField.extend({
        events: _.extend({}, AbstractField.prototype.custom_events, {
            "click .toggle_create_warning": "_onToggleCreateWarning",
        }),
        template: "WarningDropdown",
        start: function() {
            this.$view = this.$(".o_warning_conditions");
            this.$icon = this.$(".o_expand_icon");
            this._set_childs();
            return this._super.apply(this, arguments);
        },
        _set_childs: function() {
            var self = this;
            this.all_data = false;
            this.conditions = [];
            this._rpc({
                model: this.field.relation,
                method: "read",
                args: [this.value.res_ids, ["name", "create_warning"]],
            }).then(function(data) {
                self.conditions = data;
                self._fill_warnings();
            });
        },
        _fill_warnings: function() {
            this.$icon.empty();
            this.$icon.append(
                qweb.render("ExpandIcon", {
                    all_data: this.all_data,
                })
            );
            this.$view.empty();
            this.$view.append(
                qweb.render("WarningDropdownFields", {
                    conditions: this.conditions,
                    all_data: this.all_data,
                })
            );
            console.log(this.$view);
        },
        _onToggleCreateWarning: function() {
            this.all_data = !this.all_data;
            this._fill_warnings();
        },
    });
    field_registry.add("warning_dropdown", WarningDropdown);
    return WarningDropdown;
});
