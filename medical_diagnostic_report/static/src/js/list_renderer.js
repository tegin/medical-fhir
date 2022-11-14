odoo.define("medical_diagnostic_report.ListRenderer", function (require) {
    "use strict";
    var ListRenderer = require("web.ListRenderer");
    var relational_fields = require("web.relational_fields");
    ListRenderer.include({
        _renderBodyCell: function (record, node, colIndex, options) {
            if (
                node.tag === "field" &&
                node.attrs &&
                node.attrs.widget === "diagnostic_report_value" &&
                record.data.value_type
            ) {
                var final_child = undefined;
                _.each(node.children, function (child) {
                    if (child.attrs.name === "value_" + record.data.value_type) {
                        final_child = child;
                    }
                });
                if (final_child !== undefined) {
                    if (typeof final_child.attrs.modifiers !== "object") {
                        final_child.attrs.modifiers = final_child.attrs.modifiers
                            ? JSON.parse(final_child.attrs.modifiers)
                            : {};
                    }
                    return this._renderBodyCell(record, final_child, colIndex, options);
                }
            }
            return this._super.apply(this, arguments);
        },
    });
    relational_fields.FieldX2Many.include({
        init: function (parent, name, record) {
            this._super.apply(this, arguments);
            if (
                this.attrs.options.hide_delete_create &&
                record.data[this.attrs.options.hide_delete_create]
            ) {
                this.activeActions.create = false;
                this.activeActions.delete = false;
                this.activeActions.addTrashIcon = false;
            }
        },
    });
    ListRenderer.include({
        _renderBodyCell: function (record, node) {
            var $cell = this._super.apply(this, arguments);
            var isSubSection = record.data.display_type === "line_subsection";
            if (isSubSection) {
                if (node.attrs.widget === "handle") {
                    return $cell;
                } else if (node.attrs.name === "name") {
                    var nbrColumns = this._getNumberOfCols();
                    if (this.handleField) {
                        nbrColumns--;
                    }
                    if (this.addTrashIcon) {
                        nbrColumns--;
                    }
                    $cell.attr("colspan", nbrColumns);
                } else {
                    $cell.removeClass("o_invisible_modifier");
                    return $cell.addClass("o_hidden");
                }
            }
            return $cell;
        },
    });
});
