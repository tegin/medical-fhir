# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Workflow",
    "summary": "Medical workflow base",
    "version": "14.0.1.0.1",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "category": "Medical",
    "website": "https://github.com/tegin/medical-fhir",
    "license": "LGPL-3",
    "depends": ["medical_administration_practitioner", "product"],
    "data": [
        "data/ir_sequence.xml",
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "wizard/medical_add_plan_definition_views.xml",
        "views/workflow_activity_definition.xml",
        "views/workflow_plan_definition.xml",
        "views/workflow_plan_definition_action.xml",
        "views/res_config_settings_views.xml",
        "views/medical_patient.xml",
        "views/medical_request_view.xml",
        "views/medical_event_view.xml",
    ],
    "demo": ["demo/medical_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
