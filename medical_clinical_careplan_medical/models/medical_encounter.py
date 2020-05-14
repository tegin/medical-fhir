# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MedicalEncounter(models.Model):
    _inherit = "medical.encounter"

    medical_careplan_ids = fields.One2many(
        comodel_name="medical.careplan.medical", inverse_name="encounter_id"
    )
    medical_careplan_count = fields.Integer(
        compute="_compute_medical_careplan_count"
    )

    @api.depends("medical_careplan_ids")
    def _compute_medical_careplan_count(self):
        for record in self:
            record.medical_careplan_count = len(record.medical_careplan_ids)

    @api.multi
    def action_view_medical_careplans(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_careplan_medical.medical_careplan_medical_act_window"
        )
        result = action.read()[0]

        result["context"] = {
            "default_patient_id": self.patient_id.id,
            "default_encounter_id": self.id,
        }
        result["domain"] = "[('encounter_id', '=', " + str(self.id) + ")]"
        if len(self.medical_careplan_ids) == 1:
            result["views"] = [(False, "form")]
            result["res_id"] = self.medical_careplan_ids.id
        return result

    @api.constrains("patient_id")
    def _check_patient(self):
        super()._check_patient()
        if not self.env.context.get("no_check_patient", False):
            for rec in self:
                if rec.medical_careplan_ids.filtered(
                    lambda r: r.patient_id != rec.patient_id
                ):
                    raise ValidationError(_("Patient must be consistent"))
