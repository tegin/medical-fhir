odoo.define("medical_base.one2many_field", function (require) {
    "use strict";

    var relational_fields = require("web.relational_fields");
    var FormController = require("web.FormController");

    relational_fields.FieldOne2Many.include({
        _openFormDialog: function (params) {
            if (this.attrs.options.record_action) {
                var context = this.record.getContext(
                    _.extend({}, this.recordParams, {additionalContext: params.context})
                );
                return this.trigger_up(
                    "on_record_action_tree",
                    _.extend(params, {
                        record_action: this.attrs.options.record_action,
                        domain: this.record.getDomain(this.recordParams),
                        context: context,
                        field: this.field,
                        fields_view: this.attrs.views && this.attrs.views.form,
                        parentID: this.value.id,
                        viewInfo: this.view,
                        deletable: this.activeActions.delete && params.deletable,
                    })
                );
            }
            return this._super.apply(this, arguments);
        },
    });

    FormController.include({
        custom_events: _.extend({}, FormController.prototype.custom_events, {
            on_record_action_tree: "_onRecordActionTree",
        }),
        _onRecordActionTree: async function (ev) {
            ev.stopPropagation();
            var data = ev.data;
            if (data.id) {
                var record = this.model.get(data.id, {raw: true});
            }

            // Sync with the mutex to wait for potential onchanges
            await this.model.mutex.getUnlockedDef();
            var self = this;
            this._rpc({
                model: record.model,
                method: ev.data.record_action,
                args: [[record.res_id]],
                context: ev.data.context,
            }).then(function (action) {
                self.trigger_up("do_action", {
                    action: action,
                });
            });
        },
    });
});
