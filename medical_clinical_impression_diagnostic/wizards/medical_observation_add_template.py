# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalObservationAddTemplate(models.TransientModel):
    _name = "medical.observation.add.template"
    _description = "Wizard for adding templates on an observation"

    clinical_impression_id = fields.Many2one(
        "medical.clinical.impression",
        required=True,
    )
    template_id = fields.Many2one(
        "medical.observation.template",
        required=True,
    )

    def doit(self):
        self.ensure_one()
        for concept in self.template_id.concept_ids:
            if not self.clinical_impression_id.observation_ids.filtered(
                lambda r: r.concept_id == concept
            ):
                self.env["medical.observation"].create(
                    {
                        "clinical_impression_id": self.clinical_impression_id.id,
                        "concept_id": concept.id,
                        "name": concept.name,
                        "patient_id": self.clinical_impression_id.patient_id.id,
                    }
                )
        return {"type": "ir.actions.client", "tag": "soft_reload"}
