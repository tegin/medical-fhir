odoo.define("owl_tutorial_views.OWLTreeRenderer", function (require) {
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
            useSubEnv({
                saveRecord: this.saveRecord.bind(this),
            });
            if (this.props.arch.attrs.count_field) {
                Object.assign(this.state, {
                    countField: this.props.arch.attrs.count_field,
                });
            }
            console.log(this);
        }
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
    }

    const components = {
        ImpressionComponent: require("owl_tutorial_views/static/src/components/impression_component.js"),
    };
    Object.assign(OWLTreeRenderer, {
        components,
        template: "owl_tutorial_views.OWLTreeRenderer",
    });

    return patchMixin(OWLTreeRenderer);
});
