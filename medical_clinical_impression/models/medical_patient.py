# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalPatient(models.Model):

    _inherit = "medical.patient"

    medical_impression_ids = fields.One2many("medical.clinical.impression", inverse_name="patient_id")
    impression_specialty_ids = fields.Many2many("medical.specialty", compute="_compute_impression_specialties")

    @api.depends("medical_impression_ids")
    def _compute_impression_specialties(self):
        for record in self:
            record.impression_specialty_ids = record.medical_impression_ids.mapped("code")

    def action_view_clinical_impressions(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_impression."
            "medical_patient_clinical_impression_act_window"
        ).read()[0]
        action["domain"] = [
            ("patient_id", "=", self.id),
        ]
        return action
