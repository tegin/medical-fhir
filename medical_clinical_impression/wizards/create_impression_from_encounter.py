# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, fields, models


class CreateImpressionFromEncounter(models.TransientModel):

    _name = "create.impression.from.encounter"
    _description = "Create Impression From Encounter"

    patient_id = fields.Many2one(
        "medical.patient", required=True, related="encounter_id.patient_id"
    )
    specialty_id = fields.Many2one("medical.specialty", required=True)
    encounter_id = fields.Many2one(
        "medical.encounter",
        required=True,
    )
    show_encounter_warning = fields.Boolean(default=False)
    encounter_warning = fields.Char(
        default="This encounter date is more than a week ago. REVISE THE CODE",
        color="red",
        readonly=True,
    )

    def _get_impression_vals(self):
        return {
            "default_encounter_id": self.encounter_id.id,
            "default_specialty_id": self.specialty_id.id,
        }

    def generate(self):
        self.ensure_one()
        action = self.env["medical.clinical.impression"].get_formview_action()
        action["context"] = self._get_impression_vals()
        return action

    @api.onchange("encounter_id")
    def check_encounter_date(self):
        if datetime.now() - self.encounter_id.create_date >= timedelta(days=7):
            self.show_encounter_warning = True
