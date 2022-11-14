# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Clinical Request Group",
    "summary": "Medical request group",
    "version": "14.0.1.0.0",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "category": "Medical",
    "website": "https://github.com/tegin/medical-fhir",
    "license": "LGPL-3",
    "depends": ["medical_workflow"],
    "data": [
        "data/ir_sequence_data.xml",
        "security/ir.model.access.csv",
        "views/medical_request_view.xml",
        "views/medical_request_group_view.xml",
    ],
    "demo": ["demo/medical_demo.xml"],
    "installable": True,
}
