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
    medical_allergy_ids = fields.One2many(
        comodel_name="medical.condition",
        inverse_name="patient_id",
        domain=[("is_allergy", "=", True)],
        string="Allergies",
    )
    medical_allergies_count = fields.Integer(
        compute="_compute_medical_allergy_count",
        string="# of Allergies",
        domain=[("is_allergy", "=", True)],
        copy=False,
        default=0,
    )

    medical_warning_ids = fields.One2many(
        comodel_name="medical.condition",
        inverse_name="patient_id",
        string="Conditions",
        domain=[("create_warning", "=", True)],
    )

    medical_warning_count = fields.Integer(
        compute="_compute_medical_warnings_count",
        string="# of Warnings",
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

    def action_view_medical_warnings(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_condition.medical_clinical_condition_action"
        )
        result = action.read()[0]
        result["context"] = {"default_patient_id": self.id}
        result["domain"] = (
            "[('patient_id', '=', "
            + str(self.id)
            + "), ('create_warning', '=', True)]"
        )
        return result

    @api.depends("medical_warning_ids")
    def _compute_medical_warnings_count(self):
        for record in self:
            record.medical_warning_count = len(record.medical_warning_ids)

    @api.depends("medical_allergy_ids")
    def _compute_medical_allergy_count(self):
        for record in self:
            record.medical_allergies_count = len(record.medical_allergy_ids)

    def action_view_medical_allergies(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_condition.medical_clinical_condition_action"
        )
        result = action.read()[0]
        result["context"] = {
            "default_patient_id": self.id,
            "default_is_allergy": True,
        }
        result["domain"] = (
            "[('patient_id', '=', "
            + str(self.id)
            + "), ('is_allergy', '=', True)]"
        )
        return result
