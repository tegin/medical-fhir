# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalCareplanMedical(models.Model):

    _inherit = "medical.careplan.medical"

    def _action_add_message_element_procedure_vals(self, request):
        return {"procedure_request_id": request.id}

    def _action_add_message_element_vals(self):
        result = super()._action_add_message_element_vals()
        procedure_items = []
        for pr in self.procedure_request_ids:
            # TODO: Check if we need to add this
            pr_type = pr.procedure_request_result
            if not pr_type or pr_type == "medical.procedure":
                procedure_items.append(
                    (0, 0, self._action_add_message_element_procedure_vals(pr))
                )
        result["procedure_item_ids"] = procedure_items
        return result

    def _post_medical_message(self, message_text, **kwargs):
        message = super()._post_medical_message(message_text, **kwargs)
        request_ids = kwargs.get("procedure_request_ids", [])
        if request_ids:
            requests = self.env["medical.procedure.request"].browse(
                request_ids
            )
            requests._post_action_message(message)
        return message
