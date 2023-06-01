# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    routine_medication = fields.Text()

    def get_patient_data(self):
        res = super().get_patient_data()
        res["routine_medication"] = self.routine_medication
        res["id"] = self.id
        return res

    def set_routine_medication(self, routine_medication):
        self.ensure_one()
        self.routine_medication = routine_medication
        return True
