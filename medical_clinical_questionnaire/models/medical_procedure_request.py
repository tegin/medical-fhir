# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalProcedureRequest(models.Model):

    _inherit = "medical.procedure.request"

    questionnaire_id = fields.Many2one("medical.questionnaire", readonly=True,)
    questionnaire_response_ids = fields.One2many(
        "medical.questionnaire.response", inverse_name="procedure_request_id"
    )
    questionnaire_response_count = fields.Integer(
        compute="_compute_questionnaire_response_count"
    )

    @api.depends("questionnaire_response_ids")
    def _compute_questionnaire_response_count(self):
        for record in self:
            record.questionnaire_response_count = len(
                record.questionnaire_response_ids
            )

    @api.multi
    def action_view_questionnaire(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_questionnaire.medical_questionnaire_response_act_window"
        )
        result = action.read()[0]

        result["context"] = {
            "default_patient_id": self.patient_id.id,
            "default_performer_id": self.performer_id.id,
            "default_procedure_request_id": self.id,
            "default_name": self.name,
        }
        result["domain"] = (
            "[('procedure_request_id', '=', " + str(self.id) + ")]"
        )
        if len(self.questionnaire_response_ids) == 1:
            result["views"] = [(False, "form")]
            result["res_id"] = self.questionnaire_response_ids.id
        return result

    def _post_action_message(self, message):
        # TODO: Change expected date?
        return self.with_context(
            default_medical_careplan_message_id=message.id
        ).generate_events()
