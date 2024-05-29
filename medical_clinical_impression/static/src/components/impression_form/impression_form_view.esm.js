/** @odoo-module */

import {ImpressionFormController} from "./impression_form_controller.esm.js";
import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";

export const ImpressionFormView = {
    ...formView,
    Controller: ImpressionFormController,
};

registry.category("views").add("impression_form", ImpressionFormView);
