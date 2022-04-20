# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalEncounter(models.Model):

    _inherit = "medical.encounter"

    medical_impression_ids = fields.One2many(
        "medical.clinical.impression",
        inverse_name="encounter_id",
    )

    impression_specialty_ids = fields.Many2many(
        "medical.specialty", compute="_compute_impression_specialties"
    )

    family_history_ids = fields.One2many(
        "medical.family.member.history",
        related="patient_id.family_history_ids",
    )

    family_history_count = fields.Integer(
        related="patient_id.family_history_count"
    )

    @api.depends("medical_impression_ids")
    def _compute_impression_specialties(self):
        for record in self:
            record.impression_specialty_ids = (
                record.medical_impression_ids.mapped("specialty_id")
            )

    def action_view_clinical_impressions(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_impression."
            "medical_clinical_impression_act_window"
        ).read()[0]
        action["domain"] = [
            ("patient_id", "=", self.patient_id.id),
        ]
        action["context"] = {"default_encounter_id": self.id, "search_default_encounter_id": self.id}
        # TODO: should it see all mpressions or the one of this encounter?
        return action

    def action_view_family_history(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_impression."
            "medical_family_member_history_action"
        ).read()[0]
        action["domain"] = [
            ("patient_id", "=", self.patient_id.id),
        ]
        action["context"] = {"default_patient_id": self.patient_id.id}
        return action
