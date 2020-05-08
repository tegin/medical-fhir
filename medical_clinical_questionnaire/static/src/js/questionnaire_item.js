odoo.define('medical_clinical_questionnaire.QuestionnaireItemWidget', function (require) {
    "use strict";

    var QuestionnaireRenderer = require('medical.QuestionnaireRenderer');
    var relational_fields = require('web.relational_fields');

    relational_fields.FieldOne2Many.include({
        _getRenderer: function () {
            if (this.view.arch.tag === 'questionnaire') {
                return QuestionnaireRenderer;
            }
            return this._super.apply(this, arguments);
        },
        _saveQuestionnaire: function () {
            var self = this;
            _.each(this.renderer.recordWidgets, function (widget, _key) {
                self._setValue({
                    operation: 'UPDATE',
                    id: widget.dataPointID,
                    data: {result: widget.value},
                }, {notifyChange: false})
            });
        },
        commitChanges: function () {
            if (this.renderer &&
                this.renderer.viewType === "questionnaire"
            ) {
                var self = this;
                this.renderer.commitChanges().then(function () {
                    return self._saveQuestionnaire();
                });
            }
            return this._super.apply(this, arguments);
        },
    });
});
