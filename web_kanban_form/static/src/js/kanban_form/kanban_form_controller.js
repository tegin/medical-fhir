odoo.define("web_kanban_form.KanbanFormController", function (require) {
    "use strict";

    var KanbanController = require("web.KanbanController");

    var KanbanFormController = KanbanController.extend({
        template: "KanbanFormAction",

        init: function (parent, model, renderer, params) {
            this._super(...arguments);
            this.currentId = params.currentId;
        },
        willStart: async function () {
            const superPromise = this._super(...arguments);
            const viewDescr = _.findWhere(this.actionViews, {type: "form"});
            this.formView = new viewDescr.Widget(
                viewDescr.fieldsView,
                this._getFormViewOptions()
            );
            var self = this;
            return Promise.all([
                superPromise,
                (this.formController = this.formView
                    .getController(self)
                    .then(function (result) {
                        self.formController = result;
                    })),
            ]);
        },
        on_attach_callback: function () {
            this._super(...arguments);
            var node = this.$el.find(".o_form_content");
            node.empty();
            this.formController.appendTo(node);
            if (!this.currentId) {
                this.$el.find(".o_form_content").addClass("d-none");
            }
        },
        destroy: function () {
            if (this.formController) {
                this.formController.destroy();
            }
            this._super(...arguments);
        },
        _getFormViewOptions: function () {
            return {
                mode: "readonly",
                hasSelectors: false,
                hasActionMenus: true,
                modelName: this.modelName,
                controllerID: _.uniqueId("controller_"),
                withControlPanel: true,
                withSearchPanel: true,
                currentId: this.currentId,
                searchModel: this.searchModel,
            };
        },
        _onOpenRecord: function (ev) {
            ev.stopPropagation();
            var record = this.model.get(ev.data.id, {raw: true});
            var self = this;
            this.formController.trigger_up("discard_changes", {
                recordID: this.formController.handle,
                onSuccess: function () {
                    self.formController.update({currentId: record.res_id});
                    self.$el.find(".o_form_content").removeClass("d-none");
                    self.current_id = record.res_id;
                    self._pushState();
                },
            });
        },
        getState: function () {
            const state = this._super.apply(this, arguments);
            state.id = this.current_id;
            return state;
        },
    });

    return KanbanFormController;
});
