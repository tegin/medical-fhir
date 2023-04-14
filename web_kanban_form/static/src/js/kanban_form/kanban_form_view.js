odoo.define("web_kanban_form.KanbanFormView", function (require) {
    "use strict";

    var KanbanView = require("web.KanbanView");
    var KanbanFormRenderer = require("web_kanban_form.KanbanFormRenderer");
    var KanbanFormController = require("web_kanban_form.KanbanFormController");
    var viewRegistry = require("web.view_registry");

    var KanbanFormView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: KanbanFormController,
            Renderer: KanbanFormRenderer,
        }),
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
            this.controllerParams.currentId = params.currentId;
        },
    });
    viewRegistry.add("kanban_form", KanbanFormView);

    return KanbanFormView;
});
