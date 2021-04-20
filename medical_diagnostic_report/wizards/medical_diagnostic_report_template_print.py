# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalDiagnosticReportTemplatePrint(models.TransientModel):
    _name = "medical.diagnostic.report.template.print"
    _description = (
        "This wizard allows to print from template with the selected language"
    )
    diagnostic_template_id = fields.Many2one(
        "medical.diagnostic.report.template", required=True
    )
    lang = fields.Selection(
        string="Language",
        selection="_get_lang",
        required=True,
        default=lambda r: r.env.user.lang,
    )

    @api.model
    def _get_lang(self):
        return self.env["res.lang"].get_installed()

    def print(self):
        return (
            self.env.ref(
                "medical_diagnostic_report.medical_diagnostic_report_template_preview"
            )
            .with_context(lang=self.lang, force_lang=self.lang)
            .report_action(
                self.diagnostic_template_id,
                data=dict(dummy=True),
                config=False,
            )
        )
