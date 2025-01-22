# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalSpecialty(models.Model):

    _inherit = "medical.specialty"

    encounter_impression_count = fields.Integer(compute="_compute_impression_info")

    @api.depends_context("encounter_id", "patient_id")
    def _compute_impression_info(self):
        return super()._compute_impression_info()

    def _get_impression_info_patient(self):
        if self.env.context.get("encounter_id"):
            encounter_id = self.env["medical.encounter"].browse(
                self.env.context.get("encounter_id")
            )
            return encounter_id.patient_id
        return super()._get_impression_info_patient()

    def _get_impression_info(self):
        result = super()._get_impression_info()
        result["encounter_impression_count"] = 0
        if self.env.context.get("encounter_id"):
            encounter_id = self.env["medical.encounter"].browse(
                self.env.context.get("encounter_id")
            )
            result["encounter_impression_count"] = len(
                encounter_id.medical_impression_ids.filtered(
                    lambda r: r.specialty_id.id == self.id
                    and r.fhir_state != "cancelled"
                )
            )
        return result

    def get_specialty_impression(self):
        result = super().get_specialty_impression()
        if not result:
            return result
        result["context"]["default_encounter_id"] = (
            self.env.context.get("encounter_id")
            or self._get_impression_info_patient()._get_last_encounter().id
        )
        return result
