# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalPatient(models.Model):

    _inherit = "medical.patient"

    def action_view_observations_with_concept(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_diagnostic_report."
            "medical_diagnostic_report_concepts_patient_act_window"
        ).read()[0]
        action["domain"] = [
            ("diagnostic_report_id.patient_id", "=", self.id),
            ("concept_id", "!=", False),
        ]
        return action
