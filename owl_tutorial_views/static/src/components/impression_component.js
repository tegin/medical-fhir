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
                    changes: {},
                });
            }
            onValidate() {}
            onChange(ev, fieldname) {
                this.state.data.data[fieldname] = ev.target.value;
                this.state.dirty = true;
                this.state.changes[fieldname] = ev.target.value;
            }
            onEdit() {
                this.state.edit = true;
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
