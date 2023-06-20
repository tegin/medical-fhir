odoo.define(
    "medical_clinical_impression/static/src/components/impression_component.js",
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
        var Dialog = require("web.Dialog");

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
                var edit = false;
                if (this.props.currentImpression) {
                    edit =
                        parseInt(this.props.currentImpression, 10) ===
                        this.props.data.res_id;
                }
                this.state = useState({
                    edit: edit,
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
                this.FieldMany2One = relational_fields.FieldMany2One;
                this.FieldText = basic_fields.FieldText;
                this.FieldChar = basic_fields.FieldChar;
            }
            async onValidate() {
                const self = this;
                await this.onSave();
                return this.trigger("validate_record", {
                    res_id: this.state.data.res_id,
                    db_id: self.state.id,
                });
            }
            onCancel() {
                var self = this;
                return new Promise(function (resolve) {
                    Dialog.confirm(
                        self,
                        "Are you sure that you want to cancel this impression?",
                        {
                            confirm_callback: self._onCancel.bind(self),
                        }
                    ).on("closed", null, resolve);
                });
            }
            _onCancel() {
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
                this.trigger("edit_record", {id: this.state.data.res_id});
            }

            onViewExternalProcedure() {
                console.log("Viewin Procedure Rquests");
                this.trigger("view_external_procedure", {id: this.state.data.res_id});
            }

            _onCreateExternalProcedure() {
                console.log("Create Procedure Rquests");
                this.trigger("create_external_procedure", {id: this.state.data.res_id});
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

            async onSave() {
                if (this.state.dirty) {
                    await this.env.saveRecord({
                        id: this.state.data.id,
                        changes: this.state.changes,
                    });
                }
                this.state.edit = false;
                this.state.dirty = false;
                this.state.changes = {};
            }

            onDeleteChanges() {
                this.state.edit = false;
                this.state.changes = {};
                this.state.dirty = false;
                this.env.discardChanges(this.state.data.id);
            }
        }

        Object.assign(ImpressionComponent, {
            components: {FieldAdapter},
            /*
            We cannot add props on renderer on v14. We will keep the code for future versions...
            defaultProps: {
                currentImpression: undefined,
            },
            props: {
                data: {},
                currentImpression: {},
            },*/
            template: "medical_clinical_impression.ImpressionComponent",
        });

        return patchMixin(ImpressionComponent);
    }
);
