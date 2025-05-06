# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Product Request",
    "summary": """
        This addon sets the base of the medical fhir concepts
        of medication.request and device.request""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Tegin",
    "website": "https://github.com/tegin/medical-fhir",
    "depends": [
        "medical_administration_encounter",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/medical_patient.xml",
        "views/medical_encounter.xml",
        "data/ir_sequence_data.xml",
        "views/medical_product_template.xml",
        "views/medical_product_product.xml",
        "views/medical_product_administration.xml",
        "views/medical_product_request_order.xml",
        "views/medical_product_request.xml",
        "views/medication_form.xml",
        "views/medical_administration_route.xml",
    ],
    "demo": ["demo/medical_product_request_demo.xml"],
}
