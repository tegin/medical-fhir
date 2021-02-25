# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Certify",
    "summary": """
        Certify medical entities""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": ["medical_certify"],
    "data": [
        "security/ir.model.access.csv",
        "data/medical_cypher.xml",
        "views/certify_base.xml",
    ],
}
