odoo.define("owl_tutorial_views.OWLTreeController", function (require) {
    "use strict";

    var core = require("web.core");
    var BasicController = require("web.BasicController");
    var qweb = core.qweb;
    var FieldManagerMixin = require("web.FieldManagerMixin");

    var OWLTreeController = BasicController.extend({
        buttons_template: "OwlTreeView.buttons",
        custom_events: _.extend({}, BasicController.prototype.custom_events, {
            save_record: "_onSaveRecord",
            field_changed: "_onFieldChanged",
        }),
        renderButtons: function ($node) {
            if (this.noLeaf || !this.hasButtons) {
                this.hasButtons = false;
                this.$buttons = $("<div>");
            } else {
                this.$buttons = $(qweb.render(this.buttons_template, {widget: this}));
                this.$buttons.on(
                    "click",
                    ".o_owltree_button_add",
                    this._onCreateRecord.bind(this)
                );
            }
            if ($node) {
                this.$buttons.appendTo($node);
            }
        },
        _discardChanges: function (recordId) {
            var self = this;

            return this._super(...arguments).then(function () {
                console.log("HERE? ");
                self.trigger_up("field_changed", {dataPointID: recordId, changes: {}});
            });
        },
        canBeDiscarded: function () {
            return new Promise(function () {
                return true;
            });
        },
        _onFieldChanged: function (ev) {
            // Once a field has been changed, we need to send the change to the renderer,
            // it will send it to the impression components in the right way
            var self = this;
            const dataPointID = ev.data.dataPointID;
            return FieldManagerMixin._onFieldChanged
                .apply(this, arguments)
                .then(function () {
                    self.renderer.onFieldChanged({
                        dataPointID: ev.data.dataPointID,
                        data: self.model.get(dataPointID),
                        event: ev,
                    });
                });
        },
        _onCreateRecord: function (ev) {
            var self = this;
            this.do_action(
                "medical_clinical_impression.create_impression_from_patient_act_window",
                {
                    additional_context: {
                        active_id: this.model.get(this.handle).getContext().active_id,
                        impression_view: true,
                    },
                }
            );
        },
        _onSaveRecord: function (ev) {
            this.model.notifyChanges(ev.data.recordID, ev.data.changes);
            this.saveRecord(ev.data.recordID)
                .then(ev.data.onSuccess)
                .guardedCatch(ev.data.onFailure);
        },
    });

    return OWLTreeController;
});
