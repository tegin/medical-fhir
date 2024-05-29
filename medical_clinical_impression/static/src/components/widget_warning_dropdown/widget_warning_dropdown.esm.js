/** @odoo-module */
import {registry} from "@web/core/registry";
import {Component} from "@odoo/owl";
const {useState} = owl;

export class WidgetWarningDropdown extends Component {
    setup() {
        super.setup();
        this.state = useState({all_data: false});
    }

    toggleCreateWarning() {
        this.state.all_data = !this.state.all_data;
    }
}

WidgetWarningDropdown.template = "medical_clinical_impression.WidgetWarningDropdown";
registry.category("fields").add("warning_dropdown", WidgetWarningDropdown);
