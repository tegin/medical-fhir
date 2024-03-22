/** @odoo-module **/

const {Component} = owl;

import {Field} from "@web/views/fields/field";
import {registry} from "@web/core/registry";

export class DiagnosticReportValueField extends Component {
    get field_props() {
        var result = {
            name: "value_" + this.props.record.data.value_type,
            type: this.props.record.fields["value_" + this.props.record.data.value_type]
                .type,
            record: this.props.record,
        };
        if (this.props.record.data.value_type === "selection") {
            result.fieldInfo = {
                widget: "dynamic_selection_diagnostic_report",
                FieldComponent: registry
                    .category("fields")
                    .get("dynamic_selection_diagnostic_report"),
            };
        }
        return result;
    }
}

DiagnosticReportValueField.components = {Field};
DiagnosticReportValueField.template =
    "medical_diagnostic_report.DiagnosticReportValueField";

registry.category("fields").add("diagnostic_report_value", DiagnosticReportValueField);
