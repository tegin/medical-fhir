odoo.define('medical.CareplanMessageRenderer', function (require) {
    "use strict";

    var BasicRenderer = require('web.BasicRenderer');
    var field_registry = require('web.field_registry');
    var core = require('web.core');
    var time = require('web.time');
    var qweb = core.qweb;

    var CareplanMessageRenderer = BasicRenderer.extend({

        _getAvatarSource: function (res_id) {
            return '/web/image/res.partner/' + res_id + '/image_small';
        },

        _getDateAgo: function (message_date) {
            return moment(message_date).fromNow();
        },

        init: function (parent, state, params) {
            if (params === undefined) {
                params = {};
            }
            if (params.viewType === undefined ) {
                params.viewType = 'medical_message';
            }
            this._super(parent, state, params);
        },
        _renderView: function () {
            var self = this;
            var $thread = $(qweb.render('medical_message.thread'));
            var $body = $thread;
            this.$el.empty();
            $thread.appendTo(this.$el);
            _.each(this.state.data, function (data) {
                console.log(data)
                var $element = $(qweb.render(
                    'medical_message.item',
                    {
                        widget: self,
                        data: data,
                        avatar_source: self._getAvatarSource(
                            data.data.partner_creator.res_id
                        ),
                        partner_name: data.data.partner_creator.data.display_name,
                        date_ago: self._getDateAgo(data.data.message_date),
                        date_format: time.getLangDatetimeFormat(),
                    }
                ));
                var Widget = field_registry.get(data.fields.message_text.type);
                var $widget = new Widget(
                    self, 'message_text', data
                );
                $widget.appendTo($element.find('.o_medical_message_content'));
                $element.appendTo($body);
            });
            return this._super();
        },
    });

    return CareplanMessageRenderer;
});
