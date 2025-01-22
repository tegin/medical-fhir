# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Medical Clinical Impression Encounter",
    "summary": """Integrates encounters and impressions""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit, Tegin",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": [
        "medical_clinical_impression",
        "medical_clinical_condition_encounter",
    ],
    "data": [
        "security/ir.model.access.csv",
        "reports/medical_impression_report.xml",
        "wizards/create_impression_from_encounter.xml",
        "wizards/create_impression_from_patient.xml",
        "views/medical_encounter.xml",
    ],
    "demo": ["demo/medical_demo.xml"],
}
