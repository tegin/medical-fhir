# Copyright 2017 LasLabs Inc.
# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Administration Practitioner",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow, CreuBlanca, LasLabs, "
    "Odoo Community Association (OCA)",
    "category": "Medical",
    "website": "https://github.com/tegin/medical-fhir",
    "license": "LGPL-3",
    "depends": ["medical_administration"],
    "data": [
        "security/medical_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/medical_role.xml",
        "views/res_config_settings_views.xml",
        "views/medical_role.xml",
        "views/res_partner_views.xml",
        "views/medical_menu.xml",
    ],
    "demo": ["demo/medical_demo.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
}
