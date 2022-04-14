# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalPatient(models.Model):

    _inherit = "medical.patient"

    medical_impression_ids = fields.One2many(
        "medical.clinical.impression",
        inverse_name="patient_id",
    )
    impression_specialty_ids = fields.Many2many(
        "medical.specialty", compute="_compute_impression_specialties"
    )

    family_history_ids = fields.One2many(
        "medical.family.member.history", inverse_name="patient_id"
    )

    family_history_count = fields.Integer(
        compute="_compute_family_history_count"
    )

    def _compute_family_history_count(self):
        self.family_history_count = len(self.family_history_ids)

    @api.depends("medical_impression_ids")
    def _compute_impression_specialties(self):
        for record in self:
            record.impression_specialty_ids = (
                record.medical_impression_ids.mapped("specialty_id")
            )

    def action_view_clinical_impressions(self):
        self.ensure_one()
        encounter = self._get_last_encounter()
        action = self.env.ref(
            "medical_clinical_impression."
            "medical_patient_clinical_impression_act_window"
        ).read()[0]
        action["domain"] = [("patient_id", "=", self.id)]
        if encounter:
            action["context"] = {"default_encounter_id": encounter.id}
        return action

    def _get_last_encounter(self):
        if not self.encounter_ids:
            raise ValidationError(
                _("No encounters can be found for this patient")
            )
        return self.encounter_ids[0]

    def action_view_family_history(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_impression."
            "medical_family_member_history_action"
        ).read()[0]
        action["domain"] = [
            ("patient_id", "=", self.id),
        ]

        action["context"] = {"default_patient_id": self.id}
        return action
