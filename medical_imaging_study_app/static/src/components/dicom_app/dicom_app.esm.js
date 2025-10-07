/* @odoo-module */
import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

class DicomApp extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
    }
    async onClick(appId) {
        console.log("click", appId);
        const action = await this.orm.call(
            this.props.record.resModel,
            "do_app_action",
            [this.props.record.resId, appId],
            {context: this.props.record.context}
        );
        console.log(action);
        this.action.doAction(action);
    }
}
DicomApp.template = "medical_imaging_study_app.DicomApp";

registry.category("fields").add("dicom_app", DicomApp);
