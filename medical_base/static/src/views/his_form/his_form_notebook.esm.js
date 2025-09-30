/** @odoo-module **/

import {Notebook} from "@web/core/notebook/notebook";

export class HisFormNotebook extends Notebook {}
HisFormNotebook.template = "medical_base.HisFormNotebook";

HisFormNotebook.props = {
    ...Notebook.props,
    iconmap: {type: Object, optional: true},
};
HisFormNotebook.defaultProps = {
    ...Notebook.defaultProps,
    iconmap: {},
};
