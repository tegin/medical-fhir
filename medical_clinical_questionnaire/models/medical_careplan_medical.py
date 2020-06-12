# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from datetime import timedelta


class MedicalCareplanMedical(models.Model):

    _inherit = "medical.careplan.medical"

    def _action_add_message_element_procedure_vals(self, request):
        domain = []
        if not request.timing_id:
            domain = [("only_timing", "=", False)]
        possible_states = self.env[
            "medical.careplan.medical.wizard.state"
        ].search(domain)
        return {
            "procedure_request_id": request.id,
            "possible_states": [(6, 0, possible_states.ids)],
        }

    def _action_add_message_element_questionnaire_vals(self, request):
        domain = []
        if not request.timing_id:
            domain = [("only_timing", "=", False)]
        possible_states = self.env[
            "medical.careplan.medical.wizard.state"
        ].search(domain)
        return {
            "procedure_request_id": request.id,
            "possible_states": [(6, 0, possible_states.ids)],
        }

    def _action_add_message_element_questionnaire_item_vals(
        self, request, question, wizard_id=False
    ):
        return question._generate_question_vals(request, wizard_id)

    def _action_add_message_element_vals(self):
        result = super()._action_add_message_element_vals()
        procedure_items = []
        questionnaire_items = []
        # TODO: Filter procedure requests based on timing and done
        for pr in self.procedure_request_ids:
            # TODO: Check if we need to add this
            pr_type = pr.procedure_request_result
            time_ok = not pr.next_expected_date or (
                pr.next_expected_date
                < fields.Datetime.now() + timedelta(hours=1)
            )
            if (
                time_ok
                and pr.state in ("draft", "active")
                and (not pr_type or pr_type in "medical.procedure")
            ):
                procedure_items.append(
                    (0, 0, self._action_add_message_element_procedure_vals(pr))
                )
            if (
                time_ok
                and (pr_type == "medical.questionnaire.response")
                and pr.state in ("draft", "active")
            ):
                questionnaire_items.append(
                    (
                        0,
                        0,
                        self._action_add_message_element_questionnaire_vals(
                            pr
                        ),
                    )
                )
        result["procedure_item_ids"] = procedure_items
        result["questionnaire_item_ids"] = questionnaire_items
        if not (procedure_items or questionnaire_items):
            result["state"] = "final"
        # result["questionnaire_item_response_ids"] = response_items
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
                    response = item.questionnaire_response_id
                    code = item.medical_observation_code_id
                    self.env["medical.observation"].create(
                        {
                            "observation_code_id": code.id,
                            "observation_uom_id": (
                                code.default_observation_uom.id
                            ),
                            "observation_value": item.result,
                            "observation_date": response.create_date,
                            "encounter_id": (
                                response.medical_careplan_id.encounter_id.id
                            ),
                            "medical_careplan_medical_id": (
                                response.medical_careplan_id.id
                            ),
                        }
                    )
        return message
