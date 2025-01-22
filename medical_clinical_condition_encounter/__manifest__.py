# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Medical Clinical Condition Encounter",
    "summary": """Show conditions on encounter""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit, Tegin",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": ["medical_clinical_condition", "medical_administration_encounter"],
    "data": [
        "views/medical_encounter_views.xml",
    ],
    "demo": [],
    "auto_install": True,
}
