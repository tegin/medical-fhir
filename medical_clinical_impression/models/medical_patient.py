# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalPatient(models.Model):

    _inherit = "medical.patient"

    medical_impression_ids = fields.One2many(
        "medical.clinical.impression", inverse_name="patient_id"
    )
    impression_specialty_ids = fields.Many2many(
        "medical.specialty", compute="_compute_impression_specialties"
    )

    @api.depends("medical_impression_ids")
    def _compute_impression_specialties(self):
        for record in self:
            record.impression_specialty_ids = record.medical_impression_ids.mapped(
                "specialty_id"
            )

    def action_view_clinical_impressions(self):
        self.ensure_one()
        encounter = self._get_last_encounter()
        action = self.env.ref(
            "medical_clinical_impression."
            "medical_patient_clinical_impression_act_window"
        ).read()[0]
        action["domain"] = [
            ("patient_id", "=", self.id),
        ]
        if encounter:
            action["context"] = {"default_encounter_id": encounter.id}
        return action

    def _get_last_encounter(self):
        encounter = False
        self.ensure_one()
        if self.encounter_ids:
            encounter = self.encounter_ids.sorted(key=lambda r: r.create_date)[
                -1
            ]
        return encounter
