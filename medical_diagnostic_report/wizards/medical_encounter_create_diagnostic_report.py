# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalEncounterCreateDiagnosticReport(models.TransientModel):

    _name = "medical.encounter.create.diagnostic.report"

    encounter_id = fields.Many2one("medical.encounter", required=True)
    template_id = fields.Many2one(
        "medical.diagnostic.report.template", required=True
    )

    def generate(self):
        self.ensure_one()
        report = self.template_id._generate_report(self.encounter_id)
        return report.get_formview_action()
