/** @odoo-module **/

import {X2ManyField} from "@web/views/fields/x2many/x2many_field";
import {makeContext} from "@web/core/context";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class One2manyPatientField extends X2ManyField {
    setup() {
        super.setup();

        this.linkButtonText = this.env._t("Add Existing Partner");

        this.actionService = useService("action");
    }

    async onAddLink({context} = {}) {
        const record = this.props.record;
        await record.save();
        makeContext([record.getFieldContext(this.props.name), context]);
        this.actionService.doAction("medical_base.patient_partner_search_act_window", {
            additionalContext: {
                active_id: record.data.id,
            },
            onClose: async () => {
                await record.load();
                record.model.notify();
            },
        });
    }
}

One2manyPatientField.template = "medical_base.One2manyPatientField";

registry.category("fields").add("one2many_patient", One2manyPatientField);
