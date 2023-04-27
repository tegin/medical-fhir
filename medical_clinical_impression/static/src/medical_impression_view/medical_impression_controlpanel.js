/* Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
odoo.define("medical_impression.ControlPanel", function (require) {
    "use strict";

    const ControlPanel = require("web.ControlPanel");
    const patchMixin = require("web.patchMixin");

    class MedicalImpressionControlPanel extends ControlPanel {
        onFamilyHistory() {
            this.trigger("view_family_history", {});
        }
    }

    MedicalImpressionControlPanel.template =
        "medical_clinical_impression.MedicalImpressionControlPanel";
    MedicalImpressionControlPanel.props = {
        ...MedicalImpressionControlPanel.props,
        info: {
            type: Object,
            optional: 1,
        },
    };
    return patchMixin(MedicalImpressionControlPanel);
});
