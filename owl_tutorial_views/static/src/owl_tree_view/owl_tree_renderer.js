odoo.define("owl_tutorial_views.OWLTreeRenderer", function (require) {
    "use strict";

    const AbstractRendererOwl = require("web.AbstractRendererOwl");
    const patchMixin = require("web.patchMixin");
    const QWeb = require("web.QWeb");
    const session = require("web.session");

    const {useState} = owl.hooks;

    class OWLTreeRenderer extends AbstractRendererOwl {
        constructor(parent, props) {
            super(...arguments);
            this.qweb = new QWeb(this.env.isDebug(), {_s: session.origin});
            this.state = useState({
                localItems: props.items || [],
                countField: "",
            });
            if (this.props.arch.attrs.count_field) {
                Object.assign(this.state, {
                    countField: this.props.arch.attrs.count_field,
                });
            }
            console.log(this);
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
