# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from odoo import api, fields, models


class MedicalPatientCreateDiagnosticReport(models.TransientModel):

    _inherit = "medical.patient.create.diagnostic.report"

    encounter_id = fields.Many2one(
        "medical.encounter",
        required=True,
        compute="_compute_default_encounter",
    )

    @api.onchange("encounter_id")
    def check_encounter_date(self):
        if (datetime.now() - self.encounter_id.create_date) >= timedelta(days=7):
            self.show_encounter_warning = True

    @api.onchange("patient_id")
    def _compute_default_encounter(self):
        self.encounter_id = self.patient_id._get_last_encounter()
