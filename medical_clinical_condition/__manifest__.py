# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Condition",
    "summary": "Medical condition",
    "version": "14.0.1.0.0",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/medical-fhir",
    "license": "LGPL-3",
    "depends": [
        "medical_terminology_sct",
        "medical_administration_encounter",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/medical_patient_views.xml",
        "views/medical_encounter_views.xml",
        "views/medical_condition_views.xml",
        "views/medical_clinical_finding_views.xml",
        "views/medical_allergy_substance_views.xml",
    ],
    "demo": ["demo/medical_demo.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
