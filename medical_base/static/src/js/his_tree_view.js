odoo.define("medical_base.his_tree", function (require) {
    "use strict";
    var ListController = require("web.ListController");
    var ListRenderer = require("web.ListRenderer");
    var ListView = require("web.ListView");
    var viewRegistry = require("web.view_registry");
    var HisTreeRenderer = ListRenderer.extend({});
    var HisTreeController = ListController.extend({
        _onOpenRecord: function (ev) {
            ev.stopPropagation();
            var self = this;

            var record = this.model.get(ev.data.id, {raw: true});
            return self
                ._rpc({
                    model: this.modelName,
                    method: "open_medical",
                    args: [record.res_id],
                    context: record.getContext(),
                })
                .then(function (result) {
                    self.do_action(result);
                });
        },
    });

    var HisTreeView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: HisTreeController,
            Renderer: HisTreeRenderer,
        }),
    });

    viewRegistry.add("his_tree", HisTreeView);
    return {
        Controller: HisTreeController,
        View: HisTreeView,
        Renderer: HisTreeRenderer,
    };
});
