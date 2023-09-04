/* Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
odoo.define("cb_medical_clinical_impression.ControlPanelPatch", function (require) {
    "use strict";

    var Dialog = require("web.Dialog");
    var core = require("web.core");
    var _t = core._t;
    var QWeb = core.qweb;
    const MedicalImpressionControlPanel = require("medical_impression.ControlPanel");

    MedicalImpressionControlPanel.patch(
        "cb_medical_clinical_impression.ControlPanel",
        (T) =>
            class extends T {
                onEditMedication() {
                    // TODO: Open an action with the current open medication items
                }
                onEditRoutineMedication() {
                    var self = this;
                    var routine_medication_ = self.props.info.routine_medication || "";
                    var dialog = new Dialog(self, {
                        $content: $(
                            QWeb.render(
                                "cb_medical_clinical_impression.RoutineMedicationDialog",
                                {
                                    info: self.props.info,
                                    routine_medication: routine_medication_,
                                }
                            )
                        ),
                        buttons: [
                            {
                                classes: "btn-primary float-right",
                                close: true,
                                text: _t("Save"),
                                click: function () {
                                    var newValue = this.$("#routine_medication")
                                        .val()
                                        .trim();
                                    self.trigger("update_routine_medication", {
                                        res_id: self.props.info.id,
                                        routine_medication: newValue,
                                    });
                                },
                            },
                            {
                                classes: "btn-secondary float-right",
                                close: true,
                                text: _t("Discard"),
                                click: function () {
                                    console.log("Discard");
                                },
                            },
                        ],
                        size: "large",
                        title: _t("Routine Medication"),
                    }).open({shouldFocusButtons: true});
                    return dialog;
                }
            }
    );
});
