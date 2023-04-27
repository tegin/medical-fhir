odoo.define("owl_tutorial_views.OWLTreeController", function (require) {
    "use strict";

    var AbstractController = require("web.AbstractController");

    var OWLTreeController = AbstractController.extend({
        custom_events: _.extend({}, AbstractController.prototype.custom_events, {

        }),

    });

    return OWLTreeController;
});
