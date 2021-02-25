odoo.define("medical_diagnostic_report.ValueWidget", function(require) {
    "use strict";

    var field_utils = require("web.field_utils");
    var ListRenderer = require("web.ListRenderer");
    ListRenderer.include({
        init: function(parent, state, params) {
            if (parent !== undefined && parent.record !== undefined) {
                var new_context = parent.record.getContext({
                    additionalContext: parent.attrs.context || {},
                });
                if (new_context.hide_delete_create) {
                    params.addCreateLine = false;
                    params.addTrashIcon = false;
                }
            }
            this._super.apply(this, arguments);
        },
        _renderHeaderCell: function(node) {
            var $th = this._super.apply(this, arguments);
            var name = node.attrs.name;
            if (node.tag === "group" && !this.state.fields[name] && node.attrs.string) {
                $th.text(node.attrs.string);
            }
            return $th;
        },
        _renderBodyCell: function(record, node, colIndex, options) {
            if (node.tag === "group") {
                var $td = $("<td>", {class: "o_data_cell"});
                var modifiers = this._registerModifiers(
                    node,
                    record,
                    $td,
                    _.pick(options, "mode")
                );
                // If the invisible modifiers is true, the <td> element is left empty.
                // Indeed, if the modifiers was to change the whole cell would be
                // rerendered anyway.
                if (modifiers.invisible && !(options && options.renderInvisible)) {
                    return $td;
                }
                var self = this;
                _.map(node.children, function(child_node) {
                    var child_modifiers = self._registerModifiers(
                        child_node,
                        record,
                        $td,
                        _.pick(options, "mode")
                    );
                    // If the invisible modifiers is true, the <td> element is left empty.
                    // Indeed, if the modifiers was to change the whole cell would be
                    // rerendered anyway.
                    if (child_modifiers.invisible) {
                        return;
                    }
                    if (child_node.tag === "button") {
                        return $td.append(self._renderButton(record, child_node));
                    } else if (child_node.tag === "widget") {
                        return $td.append(self._renderWidget(record, child_node));
                    }
                    if (child_node.attrs.widget || (options && options.renderWidgets)) {
                        var $el = self._renderFieldWidget(
                            child_node,
                            record,
                            _.pick(options, "mode")
                        );
                        self._handleAttributes($el, child_node);
                        return $td.append($el);
                    }
                    var name = child_node.attrs.name;
                    var field = self.state.fields[name];
                    var value = record.data[name];
                    var formattedValue = field_utils.format[field.type](value, field, {
                        data: record.data,
                        escape: true,
                        isPassword: "password" in child_node.attrs,
                        digits: child_node.attrs.digits
                            ? JSON.parse(child_node.attrs.digits)
                            : undefined,
                    });
                    self._handleAttributes($td, child_node);
                    return $td.html(formattedValue);
                });
                return $td;
            }
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
                    return $cell.addClass("o_hidden");
                }
            }
            return $cell;
        },
    });
});
