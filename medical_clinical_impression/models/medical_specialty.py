# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class MedicalSpecialty(models.Model):

    _inherit = "medical.specialty"

    patient_impression_count = fields.Integer(
        compute="_compute_impression_info"
    )

    encounter_impression_count = fields.Integer(
        compute="_compute_impression_info"
    )

    impression_last_update = fields.Datetime(
        compute="_compute_impression_info"
    )

    impressions_in_progress_count = fields.Integer(
        compute="_compute_impression_info"
    )
    specialty_id = fields.Many2one(
        "medical.specialty",
        required=False,
        domain="[('specialty_id', '=', self.id)]",
    )

    def _compute_impression_info(self):
        for rec in self:
            patient_count = 0
            encounter_count = 0
            impressions_in_progress = 0
            patient_id = None
            last_update = False
            if self.env.context.get("patient_id"):
                patient_id = self.env["medical.patient"].browse(
                    self.env.context.get("patient_id")
                )
            elif self.env.context.get("encounter_id"):
                encounter_id = self.env["medical.encounter"].browse(
                    self.env.context.get("encounter_id")
                )
                encounter_count = len(
                    encounter_id.medical_impression_ids.filtered(
                        lambda r: r.specialty_id.id == rec.id
                        and r.fhir_state != "cancelled"
                    )
                )
                patient_id = encounter_id.patient_id
            if patient_id:
                patient_impression_ids = (
                    patient_id.medical_impression_ids.filtered(
                        lambda r: r.specialty_id.id == rec.id
                        and r.fhir_state != "cancelled"
                    )
                )
                patient_count = len(patient_impression_ids)
                impressions_completed = patient_impression_ids.filtered(
                    lambda r: r.fhir_state == "completed"
                )
                if impressions_completed:
                    last_update = impressions_completed[0].validation_date
                impressions_in_progress = len(
                    patient_impression_ids.filtered(
                        lambda r: r.fhir_state == "in_progress"
                    )
                )
            rec.patient_impression_count = patient_count
            rec.encounter_impression_count = encounter_count
            rec.impression_last_update = last_update
            rec.impressions_in_progress_count = impressions_in_progress

    def _get_default_context(self):
        return {"default_specialty_id": self.id}

    # The differentiation between patient_id and encounter_id
    # is just to set the default_encounter_id
    # Always pass a context to this function
    def get_specialty_impression(self):
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_clinical_impression."
            "medical_clinical_impression_act_window"
        )
        ctx_dict = self._get_default_context()
        if self.env.context.get("patient_id"):
            patient_id = self.env["medical.patient"].browse(
                self.env.context.get("patient_id")
            )
            encounter_id = patient_id._get_last_encounter()
        elif self.env.context.get("encounter_id"):
            encounter_id = self.env["medical.encounter"].browse(
                self.env.context.get("encounter_id")
            )
            patient_id = encounter_id.patient_id
        else:
            return False
        ctx_dict["default_encounter_id"] = encounter_id.id
        ctx_dict["search_default_filter_not_cancelled"] = True
        ctx_dict["active_id"] = patient_id.id
        domain = expression.AND(
            [
                safe_eval(result["domain"], ctx_dict),
                [
                    ("specialty_id", "=", self.id),
                    ("patient_id", "=", patient_id.id),
                ],
            ]
        )
        result["domain"] = domain
        result["context"] = ctx_dict
        return result
