odoo.define("cb_medical_clinical_impression.impression_component", function (require) {
    "use strict";
    const ImpressionComponent = require("medical_clinical_impression/static/src/components/impression_component.js");
    ImpressionComponent.patch(
        "cb_medical_clinical_impression.ImpressionComponent",
        (T) =>
            class extends T {
                generateDiagnosticReport() {
                    return this.trigger("create_impression_report", {
                        res_id: this.state.data.res_id,
                        db_id: this.state.data.id,
                    });
                }
            }
    );
});
