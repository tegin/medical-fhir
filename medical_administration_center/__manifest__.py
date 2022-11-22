# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Medical Administration Location",
    "version": "14.0.1.0.0",
    "category": "Medical",
    "website": "https://github.com/tegin/cb-medical",
    "author": "CreuBlanca, Eficent",
    "license": "AGPL-3",
    "depends": ["medical_administration_location"],
    "data": [
        "views/res_partner_views.xml",
        "views/medical_menu.xml",
    ],
    "demo": ["demo/medical_demo.xml"],
    "installable": True,
    "application": False,
}
