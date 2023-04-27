odoo.define(
    "owl_tutorial_views/static/src/components/impression_component.js",
    function (require) {
      "use strict";
      const { Component } = owl;
      const patchMixin = require("web.patchMixin");

      const { useState } = owl.hooks;

      class ImpressionComponent extends Component {
        /**
         * @override
         */
        constructor(...args) {
          super(...args);
          console.log(this)
          this.state = useState({});
        }
      }

      Object.assign(ImpressionComponent, {
        components: { },
        props: {
          data: {},
        },
        template: "owl_tutorial_views.ImpressionComponent",
      });

      return patchMixin(ImpressionComponent);
    }
  );
