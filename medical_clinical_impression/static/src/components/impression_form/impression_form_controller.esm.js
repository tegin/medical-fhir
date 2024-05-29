/** @odoo-module */

import {FormController} from "@web/views/form/form_controller";
import {useService} from "@web/core/utils/hooks";
import {useViewButtons} from "@web/views/view_button/view_button_hook";
const {useRef} = owl;

export class ImpressionFormController extends FormController {
    setup() {
        super.setup(...arguments);
        this.env.exposeController(this);
        this.orm = useService("orm");
        const rootRef = useRef("root");
        useViewButtons(this.model, rootRef, {
            reload: this.reloadFormController.bind(this),
            beforeExecuteAction: this.beforeExecuteActionButton.bind(this),
            afterExecuteAction: this.afterExecuteActionButton.bind(this),
        });
    }
    async reloadFormController() {
        await this.model.root.load();
        if (this.env.parentController) {
            // Refreshing
            await this.env.parentController.model.root.load();
            await this.env.parentController.render(true);
            this.env.parentController.selectRecord();
        }
    }
}
