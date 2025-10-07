# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Medical Imaging Study App",
    "summary": """Integrate webhooks Apps inside imaging studies""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Tegin",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": [
        "medical_imaging_study",
    ],
    "data": [
        "security/ir.model.access.csv",
        # 'views/medical_imaging_study.xml',
        "views/medical_imaging_app.xml",
        "views/medical_patient.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "medical_imaging_study_app/static/src/components/**/*.xml",
            "medical_imaging_study_app/static/src/components/**/*.esm.js",
        ],
    },
}
