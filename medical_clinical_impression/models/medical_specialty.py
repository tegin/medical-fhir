# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class MedicalSpecialty(models.Model):

    _inherit = "medical.specialty"

    def _get_last_encounter(self, domain):
        encounters = self.env["medical.encounter"].search(domain)
        if not encounters:
            raise ValidationError(
                _("No encounters can be found for this patient")
            )
        return encounters[0]

    def get_speciality_impression(self):
        action = self.env.ref(
            "medical_clinical_impression."
            "medical_patient_clinical_impression_act_window"
        )
        result = action.read()[0]
        if not self.env.context.get("patient_id"):
            raise ValidationError(_("Patient cannot be found"))
        encounter = self._get_last_encounter(
            [("patient_id", "=", self.env.context.get("patient_id"))]
        )
        domain = expression.AND(
            [
                result["domain"],
                [
                    ("specialty_id", "=", self.id),
                    ("patient_id", "=", self.env.context.get("patient_id")),
                ],
            ]
        )
        result["domain"] = domain
        result["context"] = {
            "default_encounter_id": encounter.id,
            "default_specialty_id": self.id,
        }
        return result
