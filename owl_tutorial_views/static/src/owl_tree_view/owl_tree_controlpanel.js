/* Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
odoo.define("owl_tree.ControlPanel", function (require) {
    "use strict";

    const ControlPanel = require("web.ControlPanel");

    const {hooks} = owl;
    const {useRef, onWillStart} = hooks;

    class OwlTreeControlPanel extends ControlPanel {
        constructor(...args) {
            super(...args);
            onWillStart(async () => {
                var data = await this.env.services.rpc({
                    model: "medical.patient",
                    method: "get_patient_data",
                    args: [[this.env.action.context.active_id]],
                });
                this.info = data;
            });
        }
    }
    OwlTreeControlPanel.template = "owl_tree.ControlPanel";
    return OwlTreeControlPanel;
});
