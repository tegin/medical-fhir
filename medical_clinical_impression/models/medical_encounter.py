# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalEncounter(models.Model):

    _inherit = "medical.encounter"

    def action_view_clinical_impressions(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_impression."
            "medical_encounter_clinical_impression_act_window"
        ).read()[0]
        action["domain"] = [
            ("encounter_id", "=", self.id),
        ]
        action["context"] = {"default_encounter_id": self.id}
        return action
