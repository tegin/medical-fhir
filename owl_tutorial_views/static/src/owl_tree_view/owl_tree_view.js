odoo.define("owl_tutorial_views.OWLTreeView", function (require) {
    "use strict";

    const OWLTreeController = require("owl_tutorial_views.OWLTreeController");
    const OWLTreeModel = require("owl_tutorial_views.OWLTreeModel");
    const OWLTreeRenderer = require("owl_tutorial_views.OWLTreeRenderer");
    const BasicView = require("web.BasicView");
    const core = require("web.core");
    const RendererWrapper = require("web.RendererWrapper");
    const view_registry = require("web.view_registry");

    const _lt = core._lt;

    class NewRendererWrapper extends RendererWrapper {
        canBeSaved() {
            return [];
        }
        commitChanges() {}
    }

    const OWLTreeView = BasicView.extend({
        accesskey: "m",
        display_name: _lt("OWLTreeView"),
        icon: "fa-indent",
        config: _.extend({}, BasicView.prototype.config, {
            Controller: OWLTreeController,
            Model: OWLTreeModel,
            Renderer: OWLTreeRenderer,
        }),
        viewType: "owl_tree",
        searchMenuTypes: ["filter", "favorite"],

        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
        },

        getRenderer(parent, state) {
            state = Object.assign(state || {}, this.rendererParams);
            return new NewRendererWrapper(parent, this.config.Renderer, state);
        },
    });

    view_registry.add("owl_tree", OWLTreeView);

    return OWLTreeView;
});
