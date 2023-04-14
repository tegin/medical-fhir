odoo.define("web_kanban_form.KanbanFormRenderer", function (require) {
    "use strict";

    var KanbanRenderer = require("web.KanbanRenderer");

    var KanbanFormRenderer = KanbanRenderer.extend({
        className: "o_kanban_view o_kanban_form_view",
    });

    return KanbanFormRenderer;
});
