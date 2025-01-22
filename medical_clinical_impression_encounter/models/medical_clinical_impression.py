# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalClinicalImpression(models.Model):
    _inherit = "medical.clinical.impression"

    encounter_id = fields.Many2one("medical.encounter", required=True, readonly=True)
    # FHIR: encounter

    patient_id = fields.Many2one(
        related="encounter_id.patient_id", readonly=True, states={}, store=True
    )
    # FHIR: patient

    current_encounter = fields.Boolean(
        help="This field is only used to stand out the impressions "
        "of the current encounter in the tree view",
        compute="_compute_current_encounter",
    )

    @api.depends("encounter_id")
    def _compute_current_encounter(self):
        for rec in self:
            current_encounter = False
            if self.env.context.get("encounter_id"):
                default_encounter = self.env.context.get("encounter_id")
                if default_encounter == rec.encounter_id.id:
                    current_encounter = True
            rec.current_encounter = current_encounter
