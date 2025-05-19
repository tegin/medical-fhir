/** @odoo-module **/

import {X2ManyField} from "@web/views/fields/x2many/x2many_field";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class MedicalX2ManyField extends X2ManyField {
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.action = useService("action");
        if (this.props.record_action) {
            this._openRecord = (params) => {
                const context = this.props.record.getFieldContext();
                this.orm
                    .call(
                        params.record.resModel,
                        this.props.record_action,
                        [[params.record.data.id]],
                        {context: context}
                    )
                    .then((action) => {
                        this.action.doAction(action);
                    });
            };
        }
    }
}
MedicalX2ManyField.props = {
    ...X2ManyField.props,
    record_action: {type: String, optional: true},
};
MedicalX2ManyField.extractProps = ({field, attrs}) => {
    return {
        ...X2ManyField.extractProps({field, attrs}),
        record_action: attrs.options.record_action,
    };
};

registry.category("fields").add("medical_one2many", MedicalX2ManyField);
