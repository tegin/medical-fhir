/** @odoo-module */

import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";
import {ImpressionKanbanRecord} from "./impression_kanban_record.esm.js";
export class ImpressionRenderer extends KanbanRenderer {}

ImpressionRenderer.components = {
    ...KanbanRenderer.components,
    KanbanRecord: ImpressionKanbanRecord,
};
ImpressionRenderer.template = "medical_clinical_impression.ImpressionRenderer";
ImpressionRenderer.props = [...KanbanRenderer.props, "selectedRecordId?"];
