# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Care plan",
    "summary": "Medical care plan",
    "version": "14.0.1.0.0",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/medical-fhir",
    "category": "Medical",
    "license": "LGPL-3",
    "depends": ["medical_clinical", "medical_workflow"],
    "data": [
        "data/ir_sequence_data.xml",
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "wizard/medical_careplan_add_plan_definition_views.xml",
        "views/medical_request_views.xml",
        "views/medical_careplan_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
