# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, fields, models


class MedicalEncounter(models.Model):
    _inherit = "medical.encounter"

    medical_condition_ids = fields.One2many(
        related="patient_id.medical_condition_ids",
    )
    medical_condition_count = fields.Integer(
        related="patient_id.medical_condition_count",
        string="# of Conditions",
    )
    medical_allergy_ids = fields.One2many(
        related="patient_id.medical_allergy_ids",
        domain=[("is_allergy", "=", True)],
    )
    medical_allergies_count = fields.Integer(
        related="patient_id.medical_allergies_count",
        string="# of Allergies",
    )

    medical_warning_ids = fields.One2many(
        related="patient_id.medical_warning_ids"
    )

    medical_warning_count = fields.Integer(
        related="patient_id.medical_warning_count",
        string="# of Warnings",
    )

    def action_view_medical_conditions(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_condition.medical_clinical_condition_action"
        )
        result = action.read()[0]
        result["context"] = {"default_patient_id": self.id}
        result["domain"] = [("patient_id", "=", self.patient_id.id)]
        return result

    def action_view_medical_warnings(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_condition.medical_warning_action"
        )
        result = action.read()[0]
        result["context"] = {"default_patient_id": self.id}
        result["domain"] = [
            ("patient_id", "=", self.patient_id.id),
            ("create_warning", "=", True),
        ]
        return result

    def action_view_medical_allergies(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_condition.medical_allergy_action"
        )
        result = action.read()[0]
        result["context"] = {
            "default_patient_id": self.id,
            "default_is_allergy": True,
        }
        result["domain"] = [
            ("patient_id", "=", self.patient_id.id),
            ("is_allergy", "=", True),
        ]

        return result

    def create_medical_clinical_condition(self):
        self.ensure_one()
        view_id = self.env.ref(
            "medical_clinical_condition." "medical_condition_view_form"
        ).id
        ctx = dict(self._context)
        is_allergy = self.env.context.get("default_is_allergy", False)
        ctx["default_is_allergy"] = is_allergy
        ctx["default_patient_id"] = self.patient_id.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "medical.condition",
            "name": _("Create clinical condition"),
            "view_type": "form",
            "view_mode": "form",
            "views": [(view_id, "form")],
            "target": "new",
            "context": ctx,
        }
