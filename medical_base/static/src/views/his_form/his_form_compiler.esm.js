/** @odoo-module **/
import {FormCompiler} from "@web/views/form/form_compiler";
import {getTag} from "@web/core/utils/xml";

export class HisFormCompiler extends FormCompiler {
    compileNotebook(el) {
        const notebook = super.compileNotebook(...arguments);
        // Force the notebook to be vertical
        notebook.setAttribute("orientation", "'vertical'");
        const icon_map = {};
        for (const child of el.children) {
            if (getTag(child, true) !== "page") {
                continue;
            }
            const icon = child.getAttribute("icon");
            const name = child.getAttribute("name");
            if (icon && name) {
                icon_map[name.replace(/'/g, "")] = icon.replace(/'/g, "");
            }
        }
        notebook.setAttribute("iconmap", JSON.stringify(icon_map));
        return notebook;
    }
    compileSheet() {
        const sheet = super.compileSheet(...arguments);
        sheet.setAttribute("class", sheet.getAttribute("class") + " o_his_form_sheet");
        return sheet;
    }
}
