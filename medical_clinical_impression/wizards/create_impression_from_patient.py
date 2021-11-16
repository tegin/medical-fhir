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
            "default_encounter_id": self.patient_id._get_last_encounter().id,
            "default_specialty_id": self.specialty_id.id,
        }

    def generate(self):
        self.ensure_one()
        action = self.env["medical.clinical.impression"].get_formview_action()
        action["context"] = self._get_impression_vals()
        return action
