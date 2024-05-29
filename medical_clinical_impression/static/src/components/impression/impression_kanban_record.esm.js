/** @odoo-module */

import {KanbanRecord} from "@web/views/kanban/kanban_record";

export class ImpressionKanbanRecord extends KanbanRecord {
    getRecordClasses() {
        var result = super.getRecordClasses();
        if (this.props.selectedRecordId === this.props.record.resId) {
            result += " o_medical_impression_selected";
        }
        return result;
    }
}
ImpressionKanbanRecord.props = [...KanbanRecord.props, "selectedRecordId?"];
