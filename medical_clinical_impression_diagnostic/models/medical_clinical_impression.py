# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalClinicalImpression(models.Model):

    _inherit = "medical.clinical.impression"

    observation_ids = fields.One2many(
        "medical.observation",
        inverse_name="clinical_impression_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    def validate_clinical_impression(self):
        res = super().validate_clinical_impression()
        for observation in self.observation_ids:
            if observation.state == "registered":
                observation.registered2final_action()
        return res

    def cancel_clinical_impression(self):
        res = super().cancel_clinical_impression()
        for observation in self.observation_ids:
            if observation.state == "registered":
                observation.cancel_action()
        return res
