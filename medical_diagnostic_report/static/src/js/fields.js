odoo.define("medical_diagnostic_report.fields", function(require) {
    "use strict";
    var FieldHtml = require("web_editor.field.html");
    /*
       This code adapts the height of an html field to the size of the content
    */
    FieldHtml.include({
        _getWysiwygOptions: function() {
            var result = this._super.apply(this, arguments);
            if (this.nodeOptions.automatic_summernote_height) {
                result.height = undefined;
            }
            return result;
        },
    });
});
