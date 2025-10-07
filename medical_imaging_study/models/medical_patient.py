# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    study_ids = fields.One2many(
        "medical.imaging.study", "patient_id", string="Imaging Studies"
    )
