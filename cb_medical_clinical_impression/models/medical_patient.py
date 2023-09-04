# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    routine_medication = fields.Text()

    def get_patient_data(self):
        res = super().get_patient_data()
        res["routine_medication"] = self.routine_medication
        medications = self.env["medical.product.request"].search(
            [
                ("category", "=", "discharge"),
                ("state", "in", ["active", "completed"]),
                ("product_type", "=", "medication"),
                ("end_date", ">=", fields.Date.today()),
                ("patient_id", "=", self.id),
            ],
        )
        res["medications"] = [
            {
                "id": medication.id,
                "product": medication.medical_product_template_id.display_name,
                "rate_quantity": medication.rate_quantity,
                "rate": medication.rate_uom_id.name,
                "end_date": medication.end_date,
            }
            for medication in medications
        ]
        res["id"] = self.id
        return res

    def set_routine_medication(self, routine_medication):
        self.ensure_one()
        self.routine_medication = routine_medication
        return True
