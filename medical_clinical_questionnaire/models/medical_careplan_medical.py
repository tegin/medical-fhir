# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalCareplanMedical(models.Model):

    _inherit = "medical.careplan.medical"

    def _action_add_message_element_procedure_vals(self, request):
        return {"procedure_request_id": request.id}

    def _action_add_message_element_questionnaire_vals(self, request):
        return {"procedure_request_id": request.id}

    def _action_add_message_element_questionnaire_item_vals(
        self, request, question
    ):
        return question._generate_question_vals(request)

    def _action_add_message_element_vals(self):
        result = super()._action_add_message_element_vals()
        procedure_items = []
        questionnaire_items = []
        response_items = []
        for pr in self.procedure_request_ids:
            # TODO: Check if we need to add this
            pr_type = pr.procedure_request_result
            if not pr_type or pr_type in "medical.procedure":
                procedure_items.append(
                    (0, 0, self._action_add_message_element_procedure_vals(pr))
                )
            if pr_type == "medical.questionnaire.response":
                questionnaire_items.append(
                    (
                        0,
                        0,
                        self._action_add_message_element_questionnaire_vals(
                            pr
                        ),
                    )
                )
                response_items += [
                    (
                        0,
                        0,
                        self._action_add_message_element_questionnaire_item_vals(
                            pr, question
                        ),
                    )
                    for question in pr.questionnaire_id.item_ids
                ]
        result["procedure_item_ids"] = procedure_items
        result["questionnaire_item_ids"] = questionnaire_items
        result["questionnaire_item_response_ids"] = response_items
        return result

    def _post_medical_message(self, message_text, **kwargs):
        message = super()._post_medical_message(message_text, **kwargs)
        request_ids = kwargs.get("procedure_request_ids", [])
        if request_ids:
            requests = self.env["medical.procedure.request"].browse(
                request_ids
            )
            requests._post_action_message(message)
        questionnaire_ids = kwargs.get("questionnaire_response_ids", [])
        if questionnaire_ids:
            questionnaire_ids = self.env[
                "medical.questionnaire.response"
            ].browse(questionnaire_ids)
            questionnaire_ids.write(
                {"medical_careplan_message_id": message.id}
            )
            for item in questionnaire_ids.mapped("item_ids"):
                if item.is_medical_observation:
                    self.env["medical.observation"].create(
                        {
                            "observation_code_id": item.medical_observation_code.id,
                            # "value": item.result,
                            # "encounter": item.result,
                        }
                    )
        return message
