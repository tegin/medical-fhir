# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class WizardAddMedicalMessage(models.TransientModel):

    _name = "wizard.add.medical.message"

    message_text = fields.Html(required=True)

    @api.multi
    def add_message(self):
        medical_careplan_id = self.env.context.get("active_id", False)
        if not medical_careplan_id:
            raise ValidationError(_("Medical Careplan not found"))
        self.env["medical.careplan.message"].create(
            {
                "user_creator": self.env.uid,
                "message_date": fields.Datetime.now(),
                "message_text": self.message_text,
                "medical_careplan_id": medical_careplan_id,
            }
        )
        return {"type": "ir.actions.act_window_close"}
