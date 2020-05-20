# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WorkflowActivityDefinition(models.Model):

    _inherit = "workflow.activity.definition"
    procedure_request_result = fields.Selection(
        selection_add=[("medical.questionnaire.response", "Questionnaire")]
    )
    questionnaire_id = fields.Many2one("medical.questionnaire")

    def _get_medical_values(
        self, vals, parent=False, plan=False, action=False
    ):
        values = super()._get_medical_values(vals, parent, plan, action)
        if (
            self.questionnaire_id
            and self.model_id.model == "medical.procedure.request"
            and self.procedure_request_result
            == "medical.questionnaire.response"
        ):
            values["questionnaire_id"] = self.questionnaire_id.id
        return values
