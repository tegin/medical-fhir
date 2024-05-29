/** @odoo-module */
const {useState, useSubEnv} = owl;
import {useBus, useService} from "@web/core/utils/hooks";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {View} from "@web/views/view";

export class ImpressionController extends KanbanController {
    async setup() {
        super.setup();
        this.state = useState({
            selectedRecordId: null,
        });
        useSubEnv({
            parentController: this,
            exposeController: this.exposeController.bind(this),
        });
        this.effect = useService("effect");
        this.orm = useService("orm");
        this.action = useService("action");
        this.router = useService("router");
        this.activeActions = this.props.archInfo.activeActions;
        this.model.addEventListener("update", () => this.selectRecord(), {once: true});
        useBus(this.env.bus, "impression:selectRecord", (ev) => {
            this.selectRecord(ev.detail);
        });
    }
    exposeController(controller) {
        this.form_controller = controller;
    }
    get viewImpressionInfo() {
        return {
            resId: this.state.selectedRecordId,
            type: "form",
            context: {
                ...(this.props.context || {}),
                form_view_ref:
                    "medical_clinical_impression.medical_clinical_impression_simple_form_view",
            },
            display: {controlPanel: false},
            mode: this.props.mode || "edit",
            resModel: this.props.resModel,
        };
    }
    async onClickNewButton() {
        const action = await this.orm.call(
            "medical.patient",
            "create_impression",
            [this.props.context.active_id],
            {
                context: this.props.context,
            }
        );
        if (action) {
            this.action.doAction(action, {
                onClose: async () => {
                    await this.model.root.load();
                    this.render(true);
                },
            });
        } else {
            await this.model.root.load();
            this.render(true);
        }
    }
    async selectRecord(record) {
        var resId = undefined;
        if (record === undefined && this.props.resId) {
            resId = this.props.resId;
        } else if (record === undefined) {
            resId = undefined;
        } else {
            resId = record.resId;
        }
        if (this.state.selectedRecordId && this.state.selectedRecordId !== resId) {
            if (this.form_controller && this.form_controller.model.root.isDirty) {
                // He tenido que añadir una condicion al principio para que no de error
                await this.form_controller.model.root.save({
                    noReload: true,
                    stayInEdition: true,
                    useSaveErrorDialog: true,
                });
                await this.model.root.load();
                await this.render(true);
            }
        }
        if (!this.state.selectedRecordId || this.state.selectedRecordId !== resId) {
            this.state.selectedRecordId = resId;
        }
        this.updateURL(resId);
    }
    async openRecord(record) {
        this.selectRecord(record);
    }
    updateURL(resId) {
        this.router.pushState({id: resId});
    }
}
ImpressionController.components = {
    ...ImpressionController.components,
    View,
};

ImpressionController.template = "medical_clinical_impression.ImpressionController";
ImpressionController.defaultProps = {};
