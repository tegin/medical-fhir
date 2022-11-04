# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_medical_administration_encounter = fields.Boolean("Encounter")
    module_medical_administration_encounter_careplan = fields.Boolean(
        "Encounter-Careplan"
    )
    module_medical_administration_location = fields.Boolean("Location")
    module_medical_administration_practitioner = fields.Boolean("Practitioner")
