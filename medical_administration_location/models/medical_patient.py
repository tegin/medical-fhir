# Copyright 2017 LasLabs Inc.
# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    medical_location_primary_id = fields.Many2one(
        string="Primary Medical Center",
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
    )
    medical_location_secondary_ids = fields.Many2many(
        string="Secondary Medical Centers",
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
    )
