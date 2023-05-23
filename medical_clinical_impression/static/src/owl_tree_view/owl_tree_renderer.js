odoo.define("medical_clinical_impression.OWLTreeRenderer", function (require) {
    "use strict";

    const AbstractRendererOwl = require("web.AbstractRendererOwl");
    const patchMixin = require("web.patchMixin");
    const QWeb = require("web.QWeb");
    const session = require("web.session");

    const {useState, useSubEnv} = owl.hooks;

    class OWLTreeRenderer extends AbstractRendererOwl {
        constructor(parent, props) {
            super(...arguments);
            this.qweb = new QWeb(this.env.isDebug(), {_s: session.origin});
            this.state = useState({
                localItems: props.items || [],
                countField: "",
            });
            // We want to send to RendererWrapper, the function of the widget
            this.env.setChild(this);
            // We want to set all the childs in order send the changes properly later
            this.childs = {};
            useSubEnv({
                saveRecord: this.saveRecord.bind(this),
                setChilds: (db_id, child) => (this.childs[db_id] = child),
                discardChanges: this.discardChanges.bind(this),
                onViewFamilyHistory: this.onViewFamilyHistory.bind(this),
            });
            if (this.props.arch.attrs.count_field) {
                Object.assign(this.state, {
                    countField: this.props.arch.attrs.count_field,
                });
            }
        }
        discardChanges(recordID) {
            return new Promise((resolve, reject) => {
                this.trigger("discard_changes", {
                    recordID,
                    onSuccess: resolve,
                    onFailure: reject,
                });
            });
        }
        // eslint-disable-next-line no-empty-function
        commitChanges() {}
        saveRecord(data) {
            return new Promise((resolve, reject) => {
                this.trigger("save_record", {
                    recordID: data.id,
                    changes: data.changes,
                    onSuccess: resolve,
                    onFailure: reject,
                });
            });
        }
        onFieldChanged({dataPointID, data, event}) {
            // We send the change only to the right children
            if (this.childs[dataPointID]) {
                this.childs[dataPointID].setData(data, event);
            }
        }
        onViewFamilyHistory(data) {
            return new Promise((resolve, reject) => {
                this.trigger("view_family_history", {
                    recordID: data.id,
                    onSuccess: resolve,
                    onFailure: reject,
                });
            });
            //this.trigger_up("view_family_history", {recordID: data.id});
        }
    }

    const components = {
        ImpressionComponent: require("medical_clinical_impression/static/src/components/impression_component.js"),
    };
    Object.assign(OWLTreeRenderer, {
        components,
        template: "medical_clinical_impression.OWLTreeRenderer",
    });

    return patchMixin(OWLTreeRenderer);
});
