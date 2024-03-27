# Copyright 2024 dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Medical Diagnostic Report Encounter",
    "summary": """
        Extends the medical_diagnostic_report funcionality""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "dixmit, Tegin",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": ["medical_administration_encounter", "medical_diagnostic_report"],
    "data": [
        "security/ir.model.access.csv",
        "wizards/medical_encounter_create_diagnostic_report.xml",
        "wizards/medical_patient_create_diagnostic_report.xml",
        "views/medical_encounter.xml",
        "views/medical_diagnostic_report.xml",
        "views/medical_patient.xml",
    ],
    "demo": [],
}
