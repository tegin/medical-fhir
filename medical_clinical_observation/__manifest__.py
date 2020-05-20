# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Clinical Observation",
    "summary": """
        Medical Clinical Observation""",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca, Odoo Community Association (OCA)",
    "website": "www.creublanca.es",
    "depends": ["medical_administration_encounter"],
    "data": [
        "security/ir.model.access.csv",
        "views/medical_observation.xml",
        "views/medical_observation_code.xml",
        "views/medical_observation_uom.xml",
    ],
}
