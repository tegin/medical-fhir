odoo.define(
    "owl_tutorial_views/static/src/components/impression_component.js",
    function (require) {
        "use strict";
        const {Component} = owl;
        const {timeFromNow} = require("mail.utils");
        const patchMixin = require("web.patchMixin");
        const {getLangDatetimeFormat} = require("web.time");
        const {useState, useSubEnv} = owl.hooks;
        const relational_fields = require("web.relational_fields");
        const basic_fields = require("web.basic_fields");
        const {ComponentAdapter} = require("web.OwlCompatibility");
        const session = require("web.session");
        var rpc = require("web.rpc");

        var core = require("web.core");
        var Dialog = require("web.Dialog");
        var _t = core._t;

        class FieldAdapter extends ComponentAdapter {
            // We need to modify the component adapter in order to define the update widget properly
            constructor(...args) {
                super(...args);
                this.env.setField(this);
            }
            updateWidget(widgetArgs) {
                var record = widgetArgs.widgetArgs[1];
                this.widget.reset(record, {target: record});
            }
        }

        class ImpressionComponent extends Component {
            /**
             * @override
             */
            constructor(...args) {
                super(...args);
                this.state = useState({
                    edit: false,
                    dirty: false,
                    data: this.props.data,
                    changes: {},
                });
                this.env.setChilds(this.props.data.id, this);
                this.fields = [];
                useSubEnv({
                    setField: (field) => this.fields.push(field),
                });
                this.FieldMany2ManyTags = relational_fields.FieldMany2ManyTags;
                this.FieldText = basic_fields.FieldText;
                this.FieldChar = basic_fields.FieldChar;
            }
            onValidate() {
                const self = this;
                return rpc
                    .query({
                        model: "medical.clinical.impression",
                        method: "validate_clinical_impression",
                        args: [[this.state.data.res_id]],
                    })
                    .then(function () {
                        self.trigger("reload", {db_id: self.state.id});
                    });
            }

            onCancel() {
                const self = this;
                return rpc
                    .query({
                        model: "medical.clinical.impression",
                        method: "cancel_clinical_impression",
                        args: [[this.state.data.res_id]],
                    })
                    .then(function () {
                        self.trigger("reload", {db_id: self.state.id});
                    });
            }
            setData(data, event) {
                // We update the data. widgets will reset themselves with `updateWidget`
                this.state.data = data;
                this.state.dirty = true;
                this.state.changes = _.extend(
                    {},
                    this.state.changes,
                    event.data.changes
                );
            }
            onEdit() {
                this.state.edit = true;
            }
            get timeFromNow() {
                if (!this.state.data.data.validation_date) {
                    return false;
                }
                return timeFromNow(this.state.data.data.validation_date);
            }

            get datetime() {
                if (!this.state.data.data.validation_date) {
                    return false;
                }
                var data = this.state.data.data.validation_date.clone();
                return data
                    .add(session.getTZOffset(data), "minutes")
                    .format(getLangDatetimeFormat());
            }

            onSave() {
                if (this.state.dirty) {
                    this.env.saveRecord({
                        id: this.state.data.id,
                        changes: this.state.changes,
                    });
                }
                this.state.edit = false;
                this.state.dirty = false;
                this.state.changes = {};
            }

            onDeleteChanges() {
                var self = this;
                /*
                Var def = new Promise(function (resolve, reject) {
                    var message = _t(
                        "You need to save this new record before editing the translation. Do you want to proceed?"
                    );
                    var dialog = Dialog.confirm(self, message, {
                        title: _t("Warning"),
                        confirm_callback: function () {
                            console.log(self);
                            self.state.edit = false;
                            resolve.call(self, true);
                        },
                        cancel_callback: reject,
                    });

                    dialog.on("closed", self, reject);
                });
                return def;*/
                return new Promise(function (resolve, reject) {
                    self.state.edit = false;
                    self.state.changes = {};
                    self.state.dirty = false;
                    self.trigger("discard_changes", {
                        recordID: self.state.data.id,
                        onSuccess: resolve,
                    });
                });
            }
        }

        Object.assign(ImpressionComponent, {
            components: {FieldAdapter},
            props: {
                data: {},
            },
            template: "owl_tutorial_views.ImpressionComponent",
        });

        return patchMixin(ImpressionComponent);
    }
);
