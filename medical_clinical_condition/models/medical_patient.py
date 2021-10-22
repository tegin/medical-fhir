# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalPatient(models.Model):
    _inherit = "medical.patient"

    medical_condition_ids = fields.One2many(
        comodel_name="medical.condition",
        inverse_name="patient_id",
        string="Conditions",
    )
    medical_condition_count = fields.Integer(
        compute="_compute_medical_condition_count",
        string="# of Conditions",
        copy=False,
        default=0,
    )

    @api.depends("medical_condition_ids")
    def _compute_medical_condition_count(self):
        for record in self:
            record.medical_condition_count = len(record.medical_condition_ids)

    def action_view_medical_conditions(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_condition.medical_clinical_condition_action"
        )
        result = action.read()[0]
        result["context"] = {"default_patient_id": self.id}
        result["domain"] = "[('patient_id', '=', " + str(self.id) + ")]"
        return result
