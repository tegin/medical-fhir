# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Medical Clinical Impression Diagnostic",
    "summary": """Allows to use observations and tempaltes from impressions""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Tegin",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": [
        "medical_clinical_impression",
        "medical_diagnostic_report",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/medical_observation_template.xml",
        "wizards/medical_observation_add_template.xml",
        "views/medical_clinical_impression.xml",
    ],
    "demo": [],
}
