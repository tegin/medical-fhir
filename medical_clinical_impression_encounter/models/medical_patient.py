# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    def action_view_clinical_impressions(self):
        action = super().action_view_clinical_impressions()
        encounter = self._get_last_encounter()
        if encounter:
            action["context"] = {
                "default_encounter_id": encounter.id,
                "search_default_filter_not_cancelled": True,
            }
        return action
