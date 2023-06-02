odoo.define("medical_clinical_impression.MedicalImpressionView", function (require) {
    "use strict";

    const MedicalImpressionController = require("medical_clinical_impression.MedicalImpressionController");
    const MedicalImpressionModel = require("medical_clinical_impression.MedicalImpressionModel");
    const MedicalImpressionRenderer = require("medical_clinical_impression.MedicalImpressionRenderer");
    const BasicView = require("web.BasicView");
    const core = require("web.core");
    const RendererWrapper = require("web.RendererWrapper");
    const view_registry = require("web.view_registry");

    const _lt = core._lt;
    const {useSubEnv} = owl.hooks;

    class NewRendererWrapper extends RendererWrapper {
        constructor(parent, props) {
            super(...arguments);
            this.view = undefined;
            useSubEnv({
                setChild: (child) => (this.view = child),
            });
        }
        canBeSaved() {
            return [];
        }
        commitChanges() {}
        onFieldChanged(ev) {
            this.view.onFieldChanged(ev);
        }
        confirmChange() {}
        selectRecord(recordId) {
            this.view.selectRecord(recordId);
        }
    }

    const MedicalImpressionView = BasicView.extend({
        accesskey: "m",
        display_name: _lt("MedicalImpressionView"),
        icon: "fa-indent",
        config: _.extend({}, BasicView.prototype.config, {
            Controller: MedicalImpressionController,
            Model: MedicalImpressionModel,
            Renderer: MedicalImpressionRenderer,
            ControlPanel: require("medical_impression.ControlPanel"),
        }),
        viewType: "medical_impression",
        searchMenuTypes: ["filter", "favorite"],

        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
        },

        getRenderer(parent, state) {
            state = Object.assign(state || {}, this.rendererParams);
            return new NewRendererWrapper(parent, this.config.Renderer, state);
        },
    });

    view_registry.add("medical_impression", MedicalImpressionView);

    return MedicalImpressionView;
});
