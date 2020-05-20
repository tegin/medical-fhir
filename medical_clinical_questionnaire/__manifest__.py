# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Clinical Questionnaire",
    "summary": """
        Create Questionnaires inside Medical Fhir as Procedure Request options""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "www.creublanca.es",
    "depends": ["medical_clinical_procedure", "medical_certify"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/medical_procedure_request.xml",
        "views/medical_questionnaire_response.xml",
        "views/medical_questionnaire.xml",
        "views/webclient_templates.xml",
        "views/workflow_activity_definition.xml",
    ],
    "qweb": ["static/src/xml/questionnaire_item.xml"],
    "demo": ["demo/questionnaire.xml"],
}
