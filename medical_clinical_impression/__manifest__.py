# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Clinical Impression",
    "summary": """
        Medical Clinical Impression based on FHIR""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "CreuBlanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": [
        "medical_workflow",
        "medical_clinical_condition",
        "medical_administration_practitioner_specialty",
        "web_ir_actions_act_multi",
        "web_ir_actions_act_view_reload",
        "medical_clinical_procedure",
    ],
    "data": [
        "views/res_users.xml",
        "views/medical_clinical_impression_template.xml",
        "views/assets.xml",
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "wizards/create_impression_from_patient.xml",
        "wizards/create_impression_from_encounter.xml",
        "views/medical_clinical_impression.xml",
        "views/medical_encounter.xml",
        "views/medical_patient.xml",
        "views/medical_clinical_finding.xml",
        "views/medical_family_member_history.xml",
        "reports/medical_impression_report.xml",
        "views/impression_view.xml",
    ],
    "qweb": [
        "static/src/xml/widget_warning_dropdown.xml",
        "static/src/xml/medical_impression_view.xml",
    ],
    "demo": [
        "demo/medical_clinical_impression_template.xml",
        "demo/medical_demo.xml",
        "demo/medical_security.xml",
    ],
}
