# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class MedicalDiagnosticReportExpand(models.TransientModel):

    _name = "medical.diagnostic.report.expand"
    _description = "This model allows to add templates to a report"

    diagnostic_report_id = fields.Many2one("medical.diagnostic.report", required=True)
    template_id = fields.Many2one("medical.diagnostic.report.template", required=True)
    template_ids = fields.Many2many(
        "medical.diagnostic.report.template",
        related="diagnostic_report_id.template_ids",
        string="Current report templates",
    )

    def merge(self):
        self.ensure_one()
        if self.diagnostic_report_id.fhir_state != "registered":
            raise ValidationError(_("Cannot update the report"))
        if self.template_id in self.diagnostic_report_id.template_ids:
            if self.env.context.get("no_raise_error_on_duplicate_template", False):
                return
            raise ValidationError(_("This template has already been imported"))
        vals = self.template_id.with_context(
            lang=self.diagnostic_report_id.lang
        )._generate_report_vals(encounter=self.diagnostic_report_id.encounter_id)
        new_vals = self._merge_new_vals(vals)
        if new_vals:
            self.diagnostic_report_id.write(new_vals)

    def _merge_new_vals(self, vals):
        new_vals = {"template_ids": vals["template_ids"]}
        if vals["with_conclusion"] and not self.diagnostic_report_id.with_conclusion:
            new_vals.update(
                {
                    "with_conclusion": vals["with_conclusion"],
                    "conclusion": vals["conclusion"],
                }
            )
        if vals["with_composition"] and not self.diagnostic_report_id.with_composition:
            new_vals.update(
                {
                    "with_composition": vals["with_composition"],
                    "composition": vals["composition"],
                }
            )

        if vals["with_observation"]:
            max_seq = 0
            if self.diagnostic_report_id.observation_ids:
                max_seq = max(
                    self.diagnostic_report_id.observation_ids.mapped("sequence")
                )

            for _a, _b, observation in vals["observation_ids"]:
                observation["sequence"] += max_seq + 1
            new_vals.update(
                {
                    "with_observation": vals["with_observation"],
                    "observation_ids": vals["observation_ids"],
                }
            )
        return new_vals
