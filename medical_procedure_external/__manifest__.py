# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Procedure External",
    "summary": """
        Allows to create external requests for patients""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": [
        "medical_workflow",
        "medical_certify",
        "medical_administration_encounter",
        "medical_clinical",
    ],
    "data": [
        "data/report_paper_format.xml",
        "data/ir_sequence_data.xml",
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "wizards/medical_encounter_create_procedure_external.xml",
        "views/menu.xml",
        "views/medical_procedure_external_request.xml",
        "views/medical_procedure_external_request_template.xml",
        "views/medical_encounter.xml",
        "views/res_users.xml",
        "reports/medical_procedure_external_request_base.xml",
        "reports/medical_procedure_external_request_template.xml",
        "reports/medical_procedure_external_request_report.xml",
        "reports/medical_procedure_external_request_template_preview.xml",
        "reports/medical_procedure_external_request_preview.xml",
        "templates/assets.xml",
    ],
    "demo": ["demo/medical_procedure_external.xml"],
}
