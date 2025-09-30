/** @odoo-module **/

import {HisFormCompiler} from "./his_form_compiler.esm";
import {HisFormRenderer} from "./his_form_renderer.esm";
import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";

export const HisFormView = {
    ...formView,
    Compiler: HisFormCompiler,
    Renderer: HisFormRenderer,
};

registry.category("views").add("his_form", HisFormView);
