# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Diagnostic Report",
    "summary": """
        Allows to create reports for patients""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": [
        "medical_administration_encounter",
        "medical_clinical",
        "medical_workflow",
        "account",
        "web_translate_dialog",
        "medical_certify",
        "web_widget_digitized_signature",
    ],
    "data": [
        "wizards/medical_diagnostic_report_expand.xml",
        "templates/assets.xml",
        "views/medical_uom.xml",
        "data/uom.xml",
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "wizards/medical_encounter_create_diagnostic_report.xml",
        "data/ir_sequence_data.xml",
        "views/medical_diagnostic_report.xml",
        "views/medical_diagnostic_report_template.xml",
        "views/medical_encounter.xml",
        "views/medical_observation_concept.xml",
        "reports/medical_diagnostic_report_base.xml",
        "reports/medical_diagnostic_report_template.xml",
        "reports/medical_diagnostic_report_report.xml",
        "reports/medical_diagnostic_report_template_preview.xml",
        "reports/medical_diagnostic_report_report_preview.xml",
    ],
    "demo": ["demo/medical_diagnostic_report.xml"],
}
