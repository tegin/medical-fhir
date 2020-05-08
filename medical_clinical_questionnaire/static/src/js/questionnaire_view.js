odoo.define('medical.QuestionnaireView', function (require) {
    "use strict";

    var BasicView = require('web.BasicView');
    var QuestionnaireRenderer = require('medical.QuestionnaireRenderer');
    var view_registry = require('web.view_registry');
    var core = require('web.core');

    var _lt = core._lt;

    var QuestionnaireView = BasicView.extend({
        accesskey: "m",
        display_name: _lt("Questionnaire"),
        icon: 'fa-file-invoice',
        viewType: 'questionnaire',
        config: _.extend({}, BasicView.prototype.config, {
            Renderer: QuestionnaireRenderer,
        }),
        multi_record: true,
        searchable: false,
    });

    view_registry.add('questionnaire', QuestionnaireView);

    return QuestionnaireView;
});
