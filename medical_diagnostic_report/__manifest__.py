# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Diagnostic Report",
    "summary": """
        Allows to create reports for patients""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA), Tegin",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": [
        "medical_base",
        "web_editor",
        "medical_certify",
        "web_widget_bokeh_chart",
        "account",
    ],
    "data": [
        "security/security.xml",
        "wizards/medical_patient_create_diagnostic_report.xml",
        "data/report_paper_format.xml",
        "security/ir.model.access.csv",
        "wizards/patient_concept_evolution.xml",
        "wizards/medical_diagnostic_report_template_print.xml",
        "wizards/medical_diagnostic_report_expand.xml",
        "views/medical_uom.xml",
        "data/uom.xml",
        "data/ir_sequence_data.xml",
        "views/medical_diagnostic_report.xml",
        "views/medical_diagnostic_report_template.xml",
        "views/medical_observation_concept.xml",
        "views/medical_patient.xml",
        "views/res_users.xml",
        "views/medical_observation_report.xml",
        "reports/medical_diagnostic_report_base.xml",
        "reports/medical_diagnostic_report_template.xml",
        "reports/medical_diagnostic_report_report.xml",
        "reports/medical_diagnostic_report_template_preview.xml",
        "reports/medical_diagnostic_report_report_preview.xml",
    ],
    "demo": ["demo/medical_diagnostic_report.xml"],
    "external_dependencies": {"python": ["numpy", "pandas"]},
    "assets": {
        "web.assets_backend": [
            "/medical_diagnostic_report/static/src/**/*.js",
            "/medical_diagnostic_report/static/src/**/*.xml",
            "/medical_diagnostic_report/static/src/**/*.scss",
        ],
        "web.report_assets_common": [
            "/medical_diagnostic_report/static/src/**/*.scss",
        ],
    },
}
