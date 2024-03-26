# Copyright 2024 dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalDiagnosticReportTemplate(models.Model):

    _inherit = "medical.diagnostic.report.template"

    def _generate_report_vals(self, encounter=None, **kwargs):
        result = super()._generate_report_vals(encounter=encounter, **kwargs)

        if encounter:
            result["encounter_id"] = encounter.id

        return result
