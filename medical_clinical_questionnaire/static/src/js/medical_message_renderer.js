odoo.define('medical_questionnaire.CareplanMessageRenderer', function (require) {
    "use strict";

    var Renderer = require('medical.CareplanMessageRenderer');
    var core = require('web.core');
    var qweb = core.qweb;

    Renderer.include({
        _generateMessageElement: function (data) {
            var $element = this._super.apply(this, arguments);
            if (data.data.procedure_message === undefined) {
                $element.find(".o_medical_message_procedures").addClass("o_hidden");
            } // This is Just In Case
            var self = this;
            $element.find('.o_medical_message_procedures').html(
                data.data.procedure_message
            );
            return $element;
        },
    });
});
