odoo.define("web_kanban_form.ActionManager", function (require) {
    "use strict";

    var ActionManager = require("web.ActionManager");
    var dom = require("web.dom");
    ActionManager.include({
        custom_events: _.extend({}, ActionManager.prototype.custom_events, {
            render_controller: "_onRenderController",
        }),
        _onRenderController: function (ev) {
            ev.stopPropagation();
            const viewType = ev.data.view_type;
            const currentController = this.getCurrentController();
            if (currentController.jsID === ev.data.controllerID) {
                // Only switch to the requested view if the controller that
                // triggered the request is the current controller
                const action = this.actions[currentController.actionID];
                // Action.controllerState = _.extend({}, action.controllerState, currentControllerState);
                const options = {
                    controllerState: action.controllerState,
                    currentId: ev.data.res_id,
                };
                if (ev.data.mode) {
                    options.mode = ev.data.mode;
                }
                this._addExtraController(action, viewType, options);
            }
        },
        _addExtraController: function (action, viewType, viewOptions) {
            var self = this;
            var view = _.findWhere(action.views, {type: viewType});
            if (!view) {
                // Can't switch to an unknown view
                return Promise.reject();
            }

            var currentController = this.getCurrentController();
            var index = undefined;
            if (currentController.actionID !== action.jsID) {
                // The requested controller is from another action, so we went back
                // to a previous action using the breadcrumbs
                var controller = _.findWhere(this.controllers, {
                    actionID: action.jsID,
                    viewType: viewType,
                });
                index = _.indexOf(this.controllerStack, controller.jsID);
            } else if (view.multiRecord) {
                // The requested controller is from the same action as the current
                // one, so we either
                //   1) go one step back from a mono record view to a multi record
                //      one using the breadcrumbs
                //   2) or we switched from a view to another  using the view
                //      switcher
                //   3) or we opened a record from a multi record view
                // Cases 1) and 2) (with multi record views): replace the first
                // controller linked to the same action in the stack
                index = _.findIndex(this.controllerStack, function (controllerID) {
                    return self.controllers[controllerID].actionID === action.jsID;
                });
            } else if (
                !_.findWhere(action.views, {type: currentController.viewType})
                    .multiRecord
            ) {
                // Case 2) (with mono record views): replace the last
                // controller by the new one if they are from the same action
                // and if they both are mono record
                index = this.controllerStack.length - 1;
            } else {
                // Case 3): insert the controller on the top of the controller
                // stack
                index = this.controllerStack.length;
            }

            var newController = function (controllerID) {
                var options = {
                    controllerID: controllerID,
                    index: index + 1,
                };
                return self
                    ._createViewController(action, viewType, viewOptions, options)
                    .then(function (cntroller) {
                        return self._startController(cntroller);
                    });
            };

            var controllerDef = action.controllers[viewType];
            if (controllerDef) {
                controllerDef = controllerDef.then(
                    function (cntroller) {
                        if (!cntroller.widget) {
                            // Lazy loaded -> load it now (with same jsID)
                            return newController(cntroller.jsID);
                        }
                        return Promise.resolve(cntroller.widget.willRestore()).then(
                            function () {
                                viewOptions = _.extend({}, viewOptions, {
                                    breadcrumbs: self._getBreadcrumbs(
                                        self.controllerStack.slice(0, index)
                                    ),
                                    shouldUpdateSearchComponents: true,
                                });
                                return cntroller.widget
                                    .reload(viewOptions)
                                    .then(function () {
                                        return cntroller;
                                    });
                            }
                        );
                    },
                    function () {
                        // If the controllerDef is rejected, it probably means that the js
                        // code or the requests made to the server crashed.  In that case,
                        // if we reuse the same promise, then the switch to the view is
                        // definitely blocked.  We want to use a new controller, even though
                        // it is very likely that it will recrash again.  At least, it will
                        // give more feedback to the user, and it could happen that one
                        // record crashes, but not another.
                        return newController();
                    }
                );
            } else {
                controllerDef = newController();
            }

            return this.dp.add(controllerDef).then(function (cntroller) {
                return self._appendFormController(currentController, cntroller);
            });
        },
        _appendFormController: function (currentController, controller) {
            var self = this;

            // Detach the current controller
            // this._detachCurrentController();

            // push the new controller to the stack at the given position, and
            // destroy controllers with an higher index
            var toDestroy = this.controllerStack.slice(controller.index);
            // Reject from the list of controllers to destroy the one that we are
            // currently pushing, or those linked to the same action as the one
            // linked to the controller that we are pushing
            toDestroy = _.reject(toDestroy, function (controllerID) {
                return (
                    controllerID === controller.jsID ||
                    self.controllers[controllerID].actionID === controller.actionID
                );
            });
            this._removeControllers(toDestroy);
            this.controllerStack = this.controllerStack.slice(0, controller.index);
            this.controllerStack.push(controller.jsID);

            // Append the new controller to the DOM
            // this._appendController(controller);
            console.log(currentController.widget.$el.find("div.o_form_content"));
            console.log(currentController.widget.$el);
            dom.append(
                currentController.widget.$el.find("div.o_form_content"),
                controller.widget.$el,
                {
                    in_DOM: this.isInDOM,
                    callbacks: [{widget: controller.widget}],
                }
            );
            /*
            If (controller.scrollPosition) {
                this.trigger_up('scrollTo', controller.scrollPosition);
            }

            // notify the environment of the new action
            this.trigger_up('current_action_updated', {
                action: this.getCurrentAction(),
                controller: controller,
            });
*/
            // close all dialogs when the current controller changes
            // core.bus.trigger('close_dialogs');

            // toggle the fullscreen mode for actions in target='fullscreen'
            // this._toggleFullscreen();
        },
    });
});
