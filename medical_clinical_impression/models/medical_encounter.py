# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class MedicalEncounter(models.Model):

    _inherit = "medical.encounter"

    medical_impression_ids = fields.One2many(
        "medical.clinical.impression",
        inverse_name="encounter_id",
    )

    impression_specialty_ids = fields.Many2many(
        "medical.specialty", related="patient_id.impression_specialty_ids"
    )

    family_history_ids = fields.One2many(
        "medical.family.member.history",
        related="patient_id.family_history_ids",
    )

    family_history_count = fields.Integer(
        related="patient_id.family_history_count"
    )

    def action_view_clinical_impressions(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_clinical_impression."
            "medical_clinical_impression_act_window"
        )
        action["domain"] = [
            ("patient_id", "=", self.patient_id.id),
        ]
        action["context"] = {
            "default_encounter_id": self.id,
            "search_default_filter_not_cancelled": True,
        }
        return action

    def action_view_family_history(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_clinical_impression."
            "medical_family_member_history_action"
        )
        action["domain"] = [
            ("patient_id", "=", self.patient_id.id),
        ]
        action["context"] = {"default_patient_id": self.patient_id.id}
        return action

    def create_family_member_history(self):
        self.ensure_one()
        view_id = self.env.ref(
            "medical_clinical_impression.medical_family_member_history_view_form"
        ).id
        ctx = dict(self._context)
        ctx["default_patient_id"] = self.patient_id.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "medical.family.member.history",
            "name": _("Create family member history"),
            "view_type": "form",
            "view_mode": "form",
            "views": [(view_id, "form")],
            "target": "new",
            "context": ctx,
        }
