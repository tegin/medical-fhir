# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Medication",
    "summary": "Medical medication base",
    "version": "14.0.1.0.0",
    "author": "CreuBlanca, ForgeFlow, Odoo Community Association (OCA)",
    "category": "Medical",
    "website": "https://github.com/tegin/medical-fhir",
    "license": "LGPL-3",
    "depends": [
        "medical_base",
        "medical_terminology_sct",
        "medical_terminology_atc",
        "product",
        "stock",
    ],
    "data": [
        "data/sct_data.xml",
        "views/medical_menu.xml",
        "views/product_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": ["demo/sct_data.xml", "demo/medication.xml"],
    "application": False,
    "installable": True,
    "auto_install": False,
}
