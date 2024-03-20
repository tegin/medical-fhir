# Copyright 2017-2022 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Base",
    "summary": "Medical Base",
    "version": "16.0.1.0.0",
    "author": "CreuBlanca, Eficent, Odoo Community Association (OCA), Tegin",
    "category": "Medical",
    "website": "https://github.com/tegin/medical-fhir",
    "license": "LGPL-3",
    "depends": ["mail", "base_fontawesome", "uom"],
    "data": [
        "wizards/patient_partner_search.xml",
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "data/ir_sequence_data.xml",
        "views/medical_menu.xml",
        "views/medical_patient.xml",
        "views/res_config_settings_views.xml",
        # "templates/assets.xml",
    ],
    "demo": ["demo/medical_demo.xml"],
    "application": True,
    "assets": {
        "web.assets_backend": [
            "medical_base/static/src/components/**/*.js",
            "medical_base/static/src/components/**/*.xml",
        ]
    },
}
