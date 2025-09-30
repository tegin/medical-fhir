/** @odoo-module **/

import {FormRenderer} from "@web/views/form/form_renderer";
import {HisFormNotebook} from "./his_form_notebook.esm";
export class HisFormRenderer extends FormRenderer {}
HisFormRenderer.components = {
    ...FormRenderer.components,
    Notebook: HisFormNotebook,
};
