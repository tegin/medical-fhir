odoo.define("owl_tutorial_views.OWLTreeController", function (require) {
    "use strict";

    var BasicController = require("web.BasicController");

    var OWLTreeController = BasicController.extend({
        custom_events: _.extend({}, BasicController.prototype.custom_events, {
            save_record: "_onSaveRecord",
        }),
        _onSaveRecord: function (ev) {
            this.model.notifyChanges(ev.data.recordID, ev.data.changes);
            this.saveRecord(ev.data.recordID)
                .then(ev.data.onSuccess)
                .guardedCatch(ev.data.onFailure);
        },
    });

    return OWLTreeController;
});
