# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class MedicalSpecialty(models.Model):

    _inherit = "medical.specialty"

    def _get_default_context(self):
        return {"default_specialty_id": self.id}

    def get_speciality_impression(self):
        action = self.env.ref(
            "medical_clinical_impression."
            "medical_clinical_impression_act_window"
        )
        result = action.read()[0]
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
            ctx_dict["search_default_encounter_id"] = encounter_id.id
        else:
            raise ValidationError(_("Patient cannot be found"))
        domain = expression.AND(
            [
                result["domain"],
                [
                    ("specialty_id", "=", self.id),
                    ("patient_id", "=", patient_id.id),
                ],
            ]
        )
        ctx_dict["default_encounter_id"] = encounter_id.id
        result["domain"] = domain
        result["context"] = ctx_dict
        return result
