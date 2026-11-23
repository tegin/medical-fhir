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

    def impression_view_prescriptions(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Prescriptions",
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "medical.product.request.order",
            "domain": [("encounter_id", "=", self.encounter_id.id)],
            "views": [
                (
                    self.env.ref(
                        "medical_product_request.medical_product_request_order_tree_view"
                    ).id,
                    "tree",
                ),
                (
                    self.env.ref(
                        "medical_product_request.medical_product_request_order_form_view"
                    ).id,
                    "form",
                ),
            ],
            "target": "current",
        }
