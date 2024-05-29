/** @odoo-module **/
// (c) 2024 Dixmit (<http://dixmit.com>)
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import {registry} from "@web/core/registry";

const actionHandlersRegistry = registry.category("action_handlers");

async function executeWindowActionSelectRecord({env, action, options}) {
    await env.services.action.doAction({type: "ir.actions.act_window_close"}, options);
    return env.bus.trigger("impression:selectRecord", {resId: action.res_id});
}

actionHandlersRegistry.add("ir.actions.impression.select_record", async (params) =>
    executeWindowActionSelectRecord(params)
);
