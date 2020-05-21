# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalCareplanMedical(models.Model):

    _name = "medical.careplan.medical"
    _description = "Medical Careplan Medical"
    _inherit = "medical.request"

    internal_identifier = fields.Char(string="Careplan")
    start_date = fields.Datetime(string="start date")  # FHIR Field: Period
    end_date = fields.Datetime(string="End date")  # FHIR Field: Period
    location_id = fields.Many2one(
        "res.partner", domain=[("is_location", "=", True)]
    )
    medical_message_ids = fields.One2many(
        "medical.careplan.message", inverse_name="medical_careplan_id"
    )

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.careplan.medical")
            or "/"
        )

    def draft2active_values(self):
        res = super().draft2active_values()
        res["start_date"] = fields.Datetime.now()
        return res

    def active2completed_values(self):
        res = super().active2completed_values()
        res["end_date"] = fields.Datetime.now()
        return res

    def _get_parent_field_name(self):
        return "medical_careplan_id"

    def action_view_request_parameters(self):
        return {
            "view": "medical_clinical_careplan.medical_careplan_action",
            "view_form": "medical.careplan.view.form",
        }

    def _action_add_message_element(self):
        return self.env["wizard.add.medical.message"].create(
            self._action_add_message_element_vals()
        )

    def _action_add_message_element_vals(self):
        return {
            "careplan_medical_id": self.id,
        }

    @api.multi
    def action_add_message(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_careplan_medical."
            "wizard_add_medical_message_act_window"
        ).read()[0]
        wizard_message = self._action_add_message_element()
        action["res_id"] = wizard_message.id
        return action

    def _post_medical_message_vals(self, message_text, **kwargs):
        return {
            "medical_careplan_id": self.id,
            "message_text": message_text,
            "user_creator": kwargs.get("user_creator", self.env.uid),
            "message_date": kwargs.get("message_date", fields.Datetime.now()),
            "location_id": kwargs.get(
                "location_id", self.location_id.id or False
            ),
        }

    def _post_medical_message(self, message_text, **kwargs):
        self.ensure_one()
        return self.env["medical.careplan.message"].create(
            self._post_medical_message_vals(message_text, **kwargs)
        )
