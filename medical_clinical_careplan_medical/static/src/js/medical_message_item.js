odoo.define('medical.MedicalMessageItemWidget', function (require) {
    "use strict";

    var CareplanMessageRenderer = require('medical.CareplanMessageRenderer');
    var relational_fields = require('web.relational_fields');

    relational_fields.FieldOne2Many.include({
        _getRenderer: function () {
            if (this.view.arch.tag === 'medical_message') {
                return CareplanMessageRenderer;
            }
            return this._super.apply(this, arguments);
        },
    });
});
