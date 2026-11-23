# Copyright 2026 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import _, fields, models
from odoo.exceptions import UserError


class MedicalPatientCreateDiagnosticReport(models.TransientModel):
    _inherit = "medical.patient.create.diagnostic.report"

    template_id = fields.Many2one(required=False)
    is_from_clinical_impression = fields.Boolean(
        default=lambda self: bool(self.env.context.get("clinical_impression_ids"))
    )

    def generate(self):
        impression_ids = self.env.context.get("clinical_impression_ids")
        if not impression_ids and not self.template_id:
            raise UserError(_("Please select a template."))
        if impression_ids and not self.template_id:
            report = self.env["medical.diagnostic.report"].create(
                {
                    "patient_id": self.patient_id.id,
                    "lang": self.lang,
                }
            )
            action = report.get_formview_action()
        else:
            action = super().generate()
        if impression_ids:
            impressions = self.env["medical.clinical.impression"].browse(impression_ids)
            summary_html = self._get_impression_summary_html(impressions)
            if summary_html:
                report = self.env[action["res_model"]].browse(action["res_id"])
                report.write(
                    {
                        "composition": (report.composition or "") + summary_html,
                        # The template may have with_composition unset, which
                        # would hide the composition field (and so the
                        # appended content) on the report form.
                        "with_composition": True,
                    }
                )
        return action

    def _get_impression_summary_html(self, impressions):
        if not impressions:
            return Markup("")
        fields_info = impressions.fields_get(["description", "summary"])
        multiple = len(impressions) > 1
        parts = []
        for impression in impressions:
            impression_parts = []
            if impression.description:
                impression_parts.append(
                    Markup("<p><b>%s</b><br/>%s</p>")
                    % (
                        fields_info["description"]["string"],
                        Markup(impression.description),
                    )
                )
            if impression.summary:
                impression_parts.append(
                    Markup("<p><b>%s</b><br/>%s</p>")
                    % (fields_info["summary"]["string"], impression.summary)
                )
            if impression_parts:
                if multiple:
                    parts.append(
                        Markup("<p><b>%s</b></p>") % impression.internal_identifier
                    )
                parts.extend(impression_parts)
        return Markup("").join(parts)
