# Copyright 2026 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import models


class MedicalPatientCreateDiagnosticReport(models.TransientModel):
    _inherit = "medical.patient.create.diagnostic.report"

    def generate(self):
        action = super().generate()
        impression_id = self.env.context.get("clinical_impression_id")
        if impression_id:
            impression = self.env["medical.clinical.impression"].browse(impression_id)
            if impression.summary:
                report = self.env[action["res_model"]].browse(action["res_id"])
                report.write(
                    {
                        "composition": (report.composition or "")
                        + self._get_impression_summary_html(impression),
                        # The template may have with_composition unset, which
                        # would hide the composition field (and so the
                        # appended summary) on the report form.
                        "with_composition": True,
                    }
                )
        return action

    def _get_impression_summary_html(self, impression):
        return Markup("<p><b>%s on %s</b><br/><i>%s</i></p>") % (
            impression.validation_user_id.name,
            impression.create_date.date(),
            impression.summary,
        )
