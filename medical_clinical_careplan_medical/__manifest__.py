# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Careplan Medical",
    "summary": """
        Medical Careplan Medical""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca, Odoo Community Association (OCA)",
    "website": "www.creublanca.es",
    "depends": [
        "mail",
        "medical_workflow",
        "medical_administration_encounter_careplan",
        "medical_clinical_observation",
    ],
    "data": [
        "wizards/wizard_add_medical_message.xml",
        "wizards/medical_careplan_medical_add_plan_definition_views.xml",
        "views/medical_careplan_message.xml",
        "views/backend_templates.xml",
        "views/medical_request.xml",
        "data/ir_sequence_data.xml",
        "security/ir.model.access.csv",
        "views/medical_careplan_medical.xml",
        "views/medical_encounter.xml",
    ],
    "qweb": ["static/src/xml/medical_message_item.xml"],
}
