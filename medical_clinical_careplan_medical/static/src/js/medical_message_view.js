odoo.define("medical.CareplanMessageView", function(require) {
    "use strict";

    var BasicView = require("web.BasicView");
    var CareplanMessageRenderer = require("medical.CareplanMessageRenderer");
    var view_registry = require("web.view_registry");
    var core = require("web.core");

    var _lt = core._lt;

    var CareplanMessageView = BasicView.extend({
        accesskey: "m",
        display_name: _lt("Medical Message"),
        icon: "fa-medkit",
        viewType: "medical_message",
        config: _.extend({}, BasicView.prototype.config, {
            Renderer: CareplanMessageRenderer,
        }),
        multi_record: true,
        searchable: false,
    });

    view_registry.add("medical_message", CareplanMessageView);

    return CareplanMessageView;
});
