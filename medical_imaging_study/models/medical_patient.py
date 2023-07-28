# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MedicalPatient(models.Model):

    _inherit = "medical.patient"

    series_ids = fields.One2many(
        comodel_name="medical.imaging.series",
        inverse_name="patient_id",
        copy=True,
        auto_join=True,
        readonly=True,
    )
