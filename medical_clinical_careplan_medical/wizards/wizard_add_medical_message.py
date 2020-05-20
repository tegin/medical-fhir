# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WizardAddMedicalMessage(models.TransientModel):

    _name = "wizard.add.medical.message"

    message_text = fields.Html()
    careplan_medical_id = fields.Many2one(
        "medical.careplan.medical", required=True
    )

    def _get_careplan_message_kwargs(self):
        return {
            "message_text": self.message_text,
        }

    def add_message(self):
        self.ensure_one()
        self.careplan_medical_id._post_medical_message(
            **self._get_careplan_message_kwargs()
        )
        return {"type": "ir.actions.act_window_close"}
