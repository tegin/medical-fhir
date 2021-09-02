# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Medical Imaging Study",
    "summary": """
        Medical Imaging Study""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "www.creublanca.es",
    "depends": [
        "medical_administration_encounter",
        "medical_clinical",
        "server_environment",
    ],
    "data": [
        "data/medical.imaging.acquisition.modality.csv",
        "security/ir.model.access.csv",
        "views/medical_imaging_study.xml",
        "views/medical_imaging_acquisition_modality.xml",
        "views/medical_imaging_endpoint.xml",
        "views/medical_imaging_storage.xml",
        "wizards/medical_imaging_import_data.xml",
    ],
    "external_dependencies": {"python": ["dicomweb_client"]},
    "demo": ["demo/medical_demo.xml"],
}
