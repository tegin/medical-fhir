# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


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
    )
    medical_allergy_ids = fields.One2many(
        comodel_name="medical.condition",
        inverse_name="patient_id",
        domain=[("is_allergy", "=", True)],
        string="Allergies",
    )
    medical_allergies_count = fields.Integer(
        compute="_compute_medical_condition_count",
        string="# of Allergies",
    )

    medical_warning_ids = fields.One2many(
        comodel_name="medical.condition",
        inverse_name="patient_id",
        string="Warnings",
        domain=[("create_warning", "=", True)],
    )

    medical_warning_count = fields.Integer(
        compute="_compute_medical_condition_count",
        string="# of Warnings",
    )

    @api.depends("medical_condition_ids")
    def _compute_medical_condition_count(self):
        for record in self:
            record.medical_condition_count = len(record.medical_condition_ids)
            record.medical_warning_count = len(record.medical_warning_ids)
            record.medical_allergies_count = len(record.medical_allergy_ids)

    def action_view_medical_conditions(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_condition.medical_clinical_condition_action"
        )
        result = action.read()[0]
        result["context"] = {"default_patient_id": self.id}
        result["domain"] = [("patient_id", "=", self.id)]
        return result

    def action_view_medical_warnings(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_condition.medical_warning_action"
        )
        result = action.read()[0]
        result["context"] = {"default_patient_id": self.id}
        result["domain"] = [
            ("patient_id", "=", self.id),
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
        result["name"] = "Allergies"
        result["domain"] = [
            ("patient_id", "=", self.id),
            ("is_allergy", "=", True),
        ]
        return result

    def _get_allergy_values(self):
        return {"is_allergy": True, "patient_id": self.id}

    # All the "crate" actions are returning an ir.actions.act.window
    # This way, if the button "discard" is clicked, the record is not saved.
    # If not, we would have a lot of records created
    # when the button is clicked by mistake.
    # All needed values are passed by "default".
    def create_allergy(self):
        self.ensure_one()
        view_id = self.env.ref(
            "medical_clinical_condition.medical_condition_view_form"
        ).id
        ctx = dict(self._context)
        vals = self._get_allergy_values()
        for key in vals:
            ctx["default_%s" % key] = vals[key]
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

    def _get_medical_clinical_condition_values(self):
        return {"patient_id": self.id}

    def create_medical_clinical_condition(self):
        self.ensure_one()
        view_id = self.env.ref(
            "medical_clinical_condition.medical_condition_view_form"
        ).id
        ctx = dict(self._context)
        vals = self._get_medical_clinical_condition_values()
        for key in vals:
            ctx["default_%s" % key] = vals[key]
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
