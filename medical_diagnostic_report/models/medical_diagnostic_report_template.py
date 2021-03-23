# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
    name = fields.Char(translate=True)
    medical_department = fields.Html(translate=True)
    composition = fields.Html(translate=True)
    conclusion = fields.Text(translate=True)

    def _generate_report_vals(self, encounter):
        return {
            "template_ids": [(4, self.id)],
            "encounter_id": encounter.id,
            "patient_name": encounter.patient_id.name,
            "vat": encounter.patient_id.vat,
            "patient_age": self._compute_age(encounter.patient_id),
            "medical_department": self.medical_department,
            "conclusion": self.conclusion,
            "composition": self.composition,
            "name": self.name,
            "lang": self.env.context.get("lang") or self.env.user.lang,
            "item_blocked": self.item_blocked,
            "with_conclusion": self.with_conclusion,
            "with_observation": self.with_observation,
            "with_composition": self.with_composition,
            "observation_ids": [
                (0, 0, item._generate_report_observation_vals(encounter))
                for item in self.item_ids
            ],
        }

    @api.model
    def _compute_age(self, patient):
        today = fields.Date.today()
        birth = patient.birth_date
        if not birth:
            return False
        age = (
            today.year
            - birth.year
            - ((today.month, today.day) < (birth.month, birth.day))
        )
        return age

    def _generate_report(self, encounter):
        return self.env["medical.diagnostic.report"].create(
            self._generate_report_vals(encounter)
        )


class MedicalDiagnosticReportTemplateItem(models.Model):

    _name = "medical.diagnostic.report.template.item"
    _inherit = ["medical.report.item.abstract"]
    _description = "Diagnostic Report Item template"
    _order = "sequence"

    template_id = fields.Many2one("medical.diagnostic.report.template")
    name = fields.Char(translate=True)
    selection_options = fields.Char(translate=True)

    def _generate_report_observation_vals(self, encounter):
        return {
            "uom_id": self.uom_id.id,
            "name": self.name,
            "reference_range_high": self.reference_range_high,
            "reference_range_low": self.reference_range_low,
            "display_type": self.display_type,
            "selection_options": self.selection_options,
            "value_type": self.value_type,
            "blocked": self.blocked or self.template_id.item_blocked,
            "sequence": self.sequence,
        }
