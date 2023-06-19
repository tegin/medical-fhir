odoo.define("medical_clinical_impression.MedicalImpressionController", function (
    require
) {
    "use strict";

    var core = require("web.core");
    var BasicController = require("web.BasicController");
    var qweb = core.qweb;
    var FieldManagerMixin = require("web.FieldManagerMixin");

    var MedicalImpressionController = BasicController.extend({
        buttons_template: "MedicalImpressionView.buttons",
        custom_events: _.extend({}, BasicController.prototype.custom_events, {
            save_record: "_onSaveRecord",
            field_changed: "_onFieldChanged",
            validate_record: "_onValidateRecord",
            view_family_history: "_onViewFamilyHistory",
            discard_button: "_onDiscardButton",
            edit_record: "_onEditRecord",
            view_procedure_requests: "_onViewProcedureRequest"
        }),
        /**
         * @override
         *
         * @param {Boolean} params.hasActionMenus
         * @param {Object} params.toolbarActions
         */
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            this.currentImpression = params.currentImpression;
            console.log(this.currentImpression);
        },
        renderButtons: function ($node) {
            if (this.noLeaf || !this.hasButtons) {
                this.hasButtons = false;
                this.$buttons = $("<div>");
            } else {
                this.$buttons = $(qweb.render(this.buttons_template, {widget: this}));
                this.$buttons.on(
                    "click",
                    ".o_medical_impression_button_add",
                    this._onCreateRecord.bind(this)
                );
            }
            if ($node) {
                this.$buttons.appendTo($node);
            }
        },
        selectRecord: function (recordId) {
            this.renderer.selectRecord(recordId);
        },
        _discardChanges: function (recordId) {
            var self = this;
            return this._super(...arguments).then(function () {
                self.trigger_up("field_changed", {
                    dataPointID: recordId,
                    changes: {},
                    doNotSetDirty: true,
                });
            });
        },
        _onDiscardButton: function (ev) {
            var self = this;
            this.discardingDef = new Promise(function (resolve) {
                resolve(true);
                self.discardingDef = null;
            });
            return this._onDiscardChanges(ev);
        },
        _onEditRecord: function (ev) {
            this.currentImpression = ev.data.id;
            this.trigger_up("push_state", {
                controllerID: this.controllerID,
                state: this.getState(),
            });
        },
        _confirmChange: function () {
            return Promise.resolve(true);
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
        _onCreateRecord: function () {
            var self = this;
            this._rpc({
                model: "medical.patient",
                method: "create_impression",
                context: this.model.loadParams.context,
                args: [[this.model.loadParams.context.active_id]],
            }).then(function (action) {
                self.do_action(action);
            });
        },
        _onSaveRecord: function (ev) {
            var self = this;
            this.saveRecord(ev.data.recordID)
                .then(ev.data.onSuccess)
                .then(function () {
                    self.currentImpression = undefined;
                    self.trigger_up("push_state", {
                        controllerID: self.controllerID,
                        state: self.getState(),
                    });
                })
                .guardedCatch(ev.data.onFailure);
        },
        updatePatientInfo() {
            var self = this;
            this._rpc({
                model: "medical.patient",
                method: "get_patient_data",
                args: [[this.model.loadParams.context.active_id]],
            }).then(function (data) {
                self.updateControlPanel({info: data});
            });
        },
        start: async function () {
            await this._super.apply(this, arguments);
            this.updatePatientInfo();
        },
        _onValidateRecord: function (ev) {
            const self = this;
            this._rpc({
                model: "medical.clinical.impression",
                method: "validate_clinical_impression",
                args: [[ev.data.res_id]],
            })
                .then(function () {
                    self.trigger_up("reload", {db_id: ev.data.db_id});
                })
                .then(function () {
                    self.updatePatientInfo();
                });
        },
        _onViewProcedureRequest: function (ev) {
            const self = this;
            console.log("Inside Controller")

            self._rpc({
                model: "medical.patient",
                method: "action_view_medical_procedure_tree",
                args: [[self.model.loadParams.context.active_id]],
            }).then(function (action) {
                console.log(action);
                self.do_action(action);
            });

        },
        _onViewFamilyHistory: function () {
            var self = this;
            self._rpc({
                model: "medical.patient",
                method: "action_view_family_history_tree",
                args: [[self.model.loadParams.context.active_id]],
            }).then(function (action) {
                self.do_action(action);
            });
        },
        /**
         * Add the current Selected impression to the state pushed in the url.
         *
         * @override
         */
        getState: function () {
            const state = this._super.apply(this, arguments);
            state.impression_id = this.currentImpression;
            return state;
        },
    });

    return MedicalImpressionController;
});
