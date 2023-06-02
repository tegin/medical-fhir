// Copyright 2017 - 2018 Modoolar <info@modoolar.com>
// Copyright 2018 Modoolar <info@modoolar.com>
// License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
odoo.define("medical_clinical_impression.ir_actions_act_select_record", function (
    require
) {
    "use strict";

    var ActionManager = require("web.ActionManager");

    ActionManager.include({
        /**
         * Intercept action handling to detect extra action type
         * @override
         */
        _handleAction: function (action, options) {
            if (action.type === "ir.actions.act_select_record") {
                console.log(action, options);
                return this._executeSelectReloadAction(action, options);
            }

            return this._super.apply(this, arguments);
        },

        /**
         * Handle 'ir.actions.act_view_reload' action
         * @returns {Promise} Resolved promise
         */
        _executeSelectReloadAction: function (action) {
            var controller = this.getCurrentController();
            if (controller && controller.widget) {
                controller.widget.reload().then(function () {
                    controller.widget.selectRecord(action.res_id);
                });
            }

            return Promise.resolve();
        },
    });
});
