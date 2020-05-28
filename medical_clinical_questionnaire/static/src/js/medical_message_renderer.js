odoo.define('medical_questionnaire.CareplanMessageRenderer', function (require) {
    "use strict";

    var Renderer = require('medical.CareplanMessageRenderer');
    var core = require('web.core');

    Renderer.include({
        _generateMessageElement: function (data) {
            var $element = this._super.apply(this, arguments);
            // This is Just In Case
            if (data.data.procedure_message === undefined) {
                $element.find(
                    ".o_medical_message_procedures"
                ).addClass("o_hidden");
            }
            $element.find('.o_medical_message_procedures').html(
                data.data.procedure_message
            );
            // This is Just In Case
            if (data.data.questionnaire_message === undefined) {
                $element.find(
                    ".o_medical_message_questionnaires"
                ).addClass("o_hidden");
            }
            $element.find('.o_medical_message_questionnaires').html(
                data.data.questionnaire_message
            );
            return $element;
        },
    });
});
