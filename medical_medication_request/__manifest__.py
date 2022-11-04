# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Medication Request",
    "summary": "Medical medication request and administration",
    "version": "14.0.1.0.0",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "category": "Medical",
    "website": "https://github.com/tegin/medical-fhir",
    "license": "LGPL-3",
    "depends": [
        "medical_workflow",
        "medical_clinical",
        "medical_medication",
        "medical_administration_location_stock",
    ],
    "data": [
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/stock_location.xml",
        "data/medical_workflow.xml",
        "views/medical_request_views.xml",
        "views/medical_medication_administration_view.xml",
        "views/medical_medication_request.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
    "auto_install": False,
}
