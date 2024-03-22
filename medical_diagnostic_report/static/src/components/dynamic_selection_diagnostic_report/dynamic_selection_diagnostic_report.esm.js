/** @odoo-module **/

import {SelectionField} from "@web/views/fields/selection/selection_field";
import {registry} from "@web/core/registry";

export class DynamicSelectionDiagnosticReportField extends SelectionField {
    get options() {
        return this.props.record.data.selection_options.split(",").map((value) => {
            return [value, value];
        });
    }

    get string() {
        console.log(this.props.value, this.options);
        return this.props.value;
    }

    onChange(ev) {
        const value = JSON.parse(ev.target.value);

        this.props.update(value);
    }
}

DynamicSelectionDiagnosticReportField.supportedTypes = ["char"];
DynamicSelectionDiagnosticReportField.legacySpecialData = undefined;

registry
    .category("fields")
    .add("dynamic_selection_diagnostic_report", DynamicSelectionDiagnosticReportField);
