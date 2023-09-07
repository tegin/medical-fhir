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
        // eslint-disable-next-line no-unused-vars
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
        /* eslint-disable no-empty-function */
        commitChanges() {}
        onFieldChanged(ev) {
            this.view.onFieldChanged(ev);
        }
        /* eslint-disable no-empty-function */
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
         * Process the fields_view to find all fields appearing in the views.
         * list those fields' name in this.fields_name, which will be the list
         * of fields read when data is fetched.
         * this.fields is the list of all field's description (the result of
         * the fields_get), where the fields appearing in the fields_view are
         * augmented with their attrs and some flags if they require a
         * particular handling.
         *
         * @param {Object} viewInfo
         * @param {Object} params
         */
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
            var impression = undefined;
            if (params.context.params) {
                impression = params.context.params.impression_id;
            }
            this.controllerParams.currentImpression = impression;
            this.rendererParams.currentImpression = impression;
        },
        getRenderer(parent, state) {
            state = Object.assign(state || {}, this.rendererParams);
            return new NewRendererWrapper(parent, this.config.Renderer, state);
        },
    });

    view_registry.add("medical_impression", MedicalImpressionView);

    return MedicalImpressionView;
});
