# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Workflow Successor",
    "summary": """
        Create successor on activity definitions""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "www.creublanca.es",
    "depends": ["medical_workflow"],
    "data": [
        "security/ir.model.access.csv",
        "views/workflow_activity_definition_successor.xml",
        "views/workflow_activity_definition.xml",
    ],
    "demo": [],
}
