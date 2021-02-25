# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalEncounterCreateDiagnosticReport(models.TransientModel):

    _name = "medical.encounter.create.diagnostic.report"
    _description = "Generate report from encounter using a template"

    encounter_id = fields.Many2one("medical.encounter", required=True)
    template_id = fields.Many2one(
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

    def generate(self):
        self.ensure_one()
        report = self.template_id.with_context(
            lang=self.lang
        )._generate_report(self.encounter_id)
        return report.get_formview_action()
