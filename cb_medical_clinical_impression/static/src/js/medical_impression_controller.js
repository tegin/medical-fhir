odoo.define("cb_medical_clinical_impression.MedicalImpressionController", function (
    require
) {
    "use strict";

    var MedicalImpressionController = require("medical_clinical_impression.MedicalImpressionController");

    MedicalImpressionController.include({
        custom_events: _.extend(
            {},
            MedicalImpressionController.prototype.custom_events,
            {
                create_impression_report: "_onCreateReportImpression",
            }
        ),
        _onCreateReportImpression(ev) {
            console.log("_generateDiagnosticReport");
            var self = this;
            self._rpc({
                model: "medical.clinical.impression",
                method: "action_create_clinical_impression_report",
                args: [[ev.data.res_id]],
            }).then(function (action) {
                self.do_action(action);
            });
        },
    });
});
