# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CreateImpressionFromPatient(models.TransientModel):
    _name = "create.impression.from.patient"
    _description = "Create Impression From Patient"
    patient_id = fields.Many2one("medical.patient", required=True)
    specialty_id = fields.Many2one("medical.specialty", required=True)

    def _get_impression_vals(self):
        return {
            "patient_id": self.patient_id.id,
            "specialty_id": self.specialty_id.id,
        }

    def generate(self):
        impression = self.env["medical.clinical.impression"].create(
            self._get_impression_vals()
        )
        if self.env.context.get("impression_view"):
            return {
                "type": "ir.actions.impression.select_record",
                "res_id": impression.id,
            }

        return self.specialty_id.with_context(
            patient_id=self.patient_id.id
        ).get_specialty_impression()
