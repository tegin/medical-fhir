# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.osv import expression


class MedicalSpecialty(models.Model):

    _inherit = "medical.specialty"

    patient_impression_count = fields.Integer(compute="_compute_impression_info")

    impression_last_update = fields.Datetime(compute="_compute_impression_info")

    impressions_in_progress_count = fields.Integer(compute="_compute_impression_info")

    @api.depends_context("patient_id")
    def _compute_impression_info(self):
        for rec in self:
            vals = rec._get_impression_info()
            rec.update(vals)

    def _get_impression_info_patient(self):
        if self.env.context.get("patient_id"):
            return self.env["medical.patient"].browse(
                self.env.context.get("patient_id")
            )
        return None

    def _get_impression_info(self):
        patient_count = 0
        impressions_in_progress = 0
        patient_id = self._get_impression_info_patient()
        last_update = False
        if patient_id:
            patient_impression_ids = patient_id.medical_impression_ids.filtered(
                lambda r: r.specialty_id.id == self.id and r.fhir_state != "cancelled"
            )
            patient_count = len(patient_impression_ids)
            impressions_completed = patient_impression_ids.filtered(
                lambda r: r.fhir_state == "completed"
            )
            if impressions_completed:
                last_update = impressions_completed[0].validation_date
            impressions_in_progress = len(
                patient_impression_ids.filtered(lambda r: r.fhir_state == "in_progress")
            )
        return {
            "patient_impression_count": patient_count,
            "impression_last_update": last_update,
            "impressions_in_progress_count": impressions_in_progress,
        }

    def _get_default_context(self):
        return {
            "default_specialty_id": self.id,
            "active_id": self.env.context.get("patient_id"),
        }

    # The differentiation between patient_id and encounter_id
    # is just to set the default_encounter_id
    # Always pass a context to this function
    def get_specialty_impression(self):
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_clinical_impression.medical_clinical_impression_act_window"
        )
        ctx_dict = self._get_default_context()
        patient_id = self._get_impression_info_patient()
        if not patient_id:
            return False
        domain = expression.AND(
            [
                result["domain"],
                [
                    ("specialty_id", "=", self.id),
                    ("patient_id", "=", patient_id.id),
                ],
            ]
        )
        ctx_dict["search_default_filter_not_cancelled"] = True
        result["domain"] = domain
        result["res_id"] = (
            self.env["medical.clinical.impression"].search(domain, limit=1).id
        )
        result["context"] = ctx_dict
        return result
