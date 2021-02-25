# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalDiagnosticReportTemplate(models.Model):

    _name = "medical.diagnostic.report.template"
    _inherit = ["medical.report.abstract"]
    _description = "Diagnostic Report Template"

    item_ids = fields.One2many(
        "medical.diagnostic.report.template.item",
        inverse_name="template_id",
        copy=True,
        string="Observations",
    )

    def _generate_report_vals(self, encounter):
        return {
            "encounter_id": encounter.id,
            "conclusion": self.conclusion,
            "name": self.name,
            "observation_ids": [
                (0, 0, item._generate_report_observation_vals(encounter))
                for item in self.item_ids
            ],
        }

    def _generate_report(self, encounter):
        return self.env["medical.diagnostic.report"].create(
            self._generate_report_vals(encounter)
        )


class MedicalDiagnosticReportTemplateItem(models.Model):

    _name = "medical.diagnostic.report.template.item"
    _inherit = ["medical.report.item.abstract"]
    _description = "Diagnostic Report Item template"

    template_id = fields.Many2one("medical.diagnostic.report.template")

    def _generate_report_observation_vals(self, encounter):
        return {
            "uom_id": self.uom_id.id,
            "name": self.name,
            "reference_range_high": self.reference_range_high,
            "reference_range_low": self.reference_range_low,
            "display_type": self.display_type,
        }
