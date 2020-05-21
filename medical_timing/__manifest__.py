# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Timing",
    "summary": """
        Create timing abstract model""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": ["medical_workflow", "medical_administration_location"],
    "data": [
        "wizards/medical_request_set_timing.xml",
        "views/medical_timing.xml",
        "data/medical_timing.xml",
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/medical_request.xml",
    ],
}
