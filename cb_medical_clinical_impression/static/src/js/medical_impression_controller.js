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
                update_routine_medication: "updateRoutineMedication",
            }
        ),
        _onCreateReportImpression(ev) {
            var self = this;
            self._rpc({
                model: "medical.clinical.impression",
                method: "action_create_clinical_impression_report",
                args: [[ev.data.res_id]],
            }).then(function (action) {
                self.do_action(action);
            });
        },
        updateRoutineMedication(ev) {
            var self = this;
            self._rpc({
                model: "medical.patient",
                method: "set_routine_medication",
                args: [[ev.data.res_id], ev.data.routine_medication],
            }).then(function (data) {
                self.updatePatientInfo();
            });
        },
    });
});
