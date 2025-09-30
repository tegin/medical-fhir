/** @odoo-module **/

import {Component} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {useFileViewer} from "../file_viewer/file_viewer_hook.esm";
import {useService} from "@web/core/utils/hooks";

export class OpenDocumentViewerField extends Component {
    setup() {
        this.orm = useService("orm");
        this.fileViewer = useFileViewer();
    }
    async openDocument() {
        this.fileViewer.open(
            await this.orm.call(this.props.record.resModel, "open_document", [
                this.props.record.resId,
            ])
        );
    }
}

OpenDocumentViewerField.template = "medical_base.OpenDocumentViewerField";

registry.category("fields").add("open_document_viewer", OpenDocumentViewerField);
