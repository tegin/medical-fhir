odoo.define(
    "owl_tutorial_views/static/src/components/impression_component.js",
    function (require) {
        "use strict";
        const {Component} = owl;
        const patchMixin = require("web.patchMixin");

        const {useState} = owl.hooks;

        class ImpressionComponent extends Component {
            /**
             * @override
             */
            constructor(...args) {
                super(...args);
                console.log(this);
                this.state = useState({
                    edit: false,
                    dirty: false,
                    data: this.props.data,
                });
            }
            onValidate() {}
            onChange(ev, fieldname) {
                this.state.data.data[fieldname] = ev.target.value;
                this.state.dirty = true;
                console.log(this);
            }
            onEdit() {
                this.state.edit = true;
            }
            onSave() {
                // TODO: SEND SAVE!!!
                this.state.edit = false;
                this.state.dirty = false;
            }
        }

        Object.assign(ImpressionComponent, {
            components: {},
            props: {
                data: {},
            },
            template: "owl_tutorial_views.ImpressionComponent",
        });

        return patchMixin(ImpressionComponent);
    }
);
