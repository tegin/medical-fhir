# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from odoo import api, fields, models


class CreateImpressionFromPatient(models.TransientModel):
    _inherit = "create.impression.from.patient"
    _description = "Create Impression From Patient"

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
        result = super()._get_impression_vals()
        result["encounter_id"] = self.encounter_id.id
        return result

    @api.onchange("patient_id")
    @api.depends_context("default_encounter_id")
    def _compute_default_encounter(self):
        for record in self:
            if self.env.context.get("default_encounter_id"):
                record.encounter_id = self.env.context.get("default_encounter_id")
            else:
                record.encounter_id = record.patient_id._get_last_encounter()

    @api.onchange("encounter_id")
    def _onchange_encounter_date(self):
        if datetime.now() - self.encounter_id.create_date >= timedelta(days=7):
            self.show_encounter_warning = True
