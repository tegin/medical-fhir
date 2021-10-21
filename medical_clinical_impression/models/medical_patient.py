# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalPatient(models.Model):

    _inherit = "medical.patient"

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
