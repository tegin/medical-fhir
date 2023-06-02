# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, fields, models


class CreateImpressionFromPatient(models.TransientModel):

    _name = "create.impression.from.patient"
    _description = "Create Impression From Patient"

    patient_id = fields.Many2one("medical.patient", required=True)

    specialty_id = fields.Many2one("medical.specialty", required=True)
    encounter_id = fields.Many2one(
        "medical.encounter",
        required=True,
        compute="_compute_default_encounter",
    )
    show_encounter_warning = fields.Boolean(default=False)
    encounter_warning = fields.Char(
        default="This encounter date is more than a week ago. REVIEW THE CODE",
        readonly=True,
    )

    def _get_impression_vals(self):
        return {
            "encounter_id": self.encounter_id.id,
            "specialty_id": self.specialty_id.id,
        }

    def generate(self):
        self.ensure_one()
        impression = self.env["medical.clinical.impression"].create(
            self._get_impression_vals()
        )
        if self.env.context.get("impression_view"):
            return {
                "type": "ir.actions.act_multi",
                "actions": [
                    {"type": "ir.actions.act_window_close"},
                    {
                        "type": "ir.actions.act_select_record",
                        "res_id": impression.id,
                    },
                ],
            }
        return self.specialty_id.with_context(
            patient_id=self.patient_id.id
        ).get_specialty_impression()

    @api.onchange("patient_id")
    def _compute_default_encounter(self):
        self.encounter_id = self.patient_id._get_last_encounter()

    @api.onchange("encounter_id")
    def _onchange_encounter_date(self):
        if datetime.now() - self.encounter_id.create_date >= timedelta(days=7):
            self.show_encounter_warning = True
