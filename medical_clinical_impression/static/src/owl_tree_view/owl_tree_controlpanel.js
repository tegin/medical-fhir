/* Copyright 2022 Tecnativa - Alexandre D. Díaz
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */
odoo.define("owl_tree.ControlPanel", function (require) {
    "use strict";

    const ControlPanel = require("web.ControlPanel");

    class OwlTreeControlPanel extends ControlPanel {}
    OwlTreeControlPanel.template = "owl_tree.ControlPanel";
    OwlTreeControlPanel.props = {
        ...OwlTreeControlPanel.props,
        info: {
            type: Object,
            optional: 1,
        },
    };
    return OwlTreeControlPanel;
});
