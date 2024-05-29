/** @odoo-module */

import {ImpressionController} from "./impression_controller.esm.js";
import {ImpressionRenderer} from "./impression_renderer.esm.js";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";

export const impressionView = {
    ...kanbanView,
    Renderer: ImpressionRenderer,
    Controller: ImpressionController,
    buttonTemplate: "medical_clinical_impression.ImpressionView.Buttons",
    searchMenuTypes: ["filter"],
};

registry.category("views").add("impression", impressionView);
