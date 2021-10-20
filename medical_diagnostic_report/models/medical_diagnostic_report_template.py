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
    name = fields.Char(required=True)
    title = fields.Char(translate=True)
    composition = fields.Html(translate=True, sanitize=False)
    conclusion = fields.Text(translate=True)
    active = fields.Boolean(default=True)

    def _generate_report_vals(self, encounter=None, **kwargs):
        return {
            "template_ids": [(4, self.id)],
            "encounter_id": encounter.id,
            "patient_name": encounter.patient_id.name,
            "vat": encounter.patient_id.vat,
            "patient_age": self._compute_age(encounter.patient_id),
            "conclusion": self.conclusion,
            "composition": self.composition,
            "name": self.title or self.name,
            "lang": self.env.context.get("lang") or self.env.user.lang,
            "item_blocked": self.item_blocked,
            "with_conclusion": self.with_conclusion,
            "with_observation": self.with_observation,
            "with_composition": self.with_composition,
            "observation_ids": [
                (
                    0,
                    0,
                    item._generate_report_observation_vals(
                        encounter=encounter, **kwargs
                    ),
                )
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

    def _generate_report(self, **kwargs):
        return self.env["medical.diagnostic.report"].create(
            self._generate_report_vals(**kwargs)
        )


class MedicalDiagnosticReportTemplateItem(models.Model):

    _name = "medical.diagnostic.report.template.item"
    _inherit = ["medical.report.item.abstract"]
    _description = "Diagnostic Report Item template"
    _order = "sequence, id"

    template_id = fields.Many2one("medical.diagnostic.report.template")
    name = fields.Char(translate=True)
    selection_options = fields.Char(translate=True)
    reference_range_low_view = fields.Float(
        compute="_compute_from_concept", inverse="_inverse_reference_range_low"
    )
    reference_range_high_view = fields.Float(
        compute="_compute_from_concept",
        inverse="_inverse_reference_range_high",
    )
    view_uom_id = fields.Many2one(
        "uom.uom", compute="_compute_from_concept", inverse="_inverse_uom_id"
    )
    value_type_view = fields.Selection(
        selection=lambda r: r.env["medical.report.item.abstract"]
        ._fields["value_type"]
        .selection,
        compute="_compute_from_concept",
        inverse="_inverse_value_type",
    )

    _sql_constraints = [
        (
            "concept_id_uniq",
            "UNIQUE (concept_id, template_id)",
            "Observation concept must be unique.",
        ),
        (
            "check_reference_range",
            "CHECK(concept_id is not null "
            "or reference_range_low <= reference_range_high)",
            "Reference range low cannot be larger that reference range high",
        ),
    ]

    @api.depends(
        "concept_id",
        "concept_id.reference_range_high",
        "concept_id.reference_range_low",
        "concept_id.value_type",
        "concept_id.uom_id",
        "reference_range_high",
        "reference_range_low",
        "value_type",
        "uom_id",
    )
    def _compute_from_concept(self):
        for record in self:
            concept = record.concept_id or record
            record.reference_range_high_view = concept.reference_range_high
            record.reference_range_low_view = concept.reference_range_low
            record.view_uom_id = concept.uom_id
            record.value_type_view = concept.value_type

    def _inverse_reference_range_low(self):
        for record in self:
            if not record.concept_id:
                record.reference_range_low = record.reference_range_low_view

    def _inverse_value_type(self):
        for record in self:
            if not record.concept_id:
                record.value_type = record.value_type_view

    def _inverse_reference_range_high(self):
        for record in self:
            if not record.concept_id:
                record.reference_range_high = record.reference_range_high_view

    def _inverse_uom_id(self):
        for record in self:
            if not record.concept_id:
                record.uom_id = record.view_uom_id

    def _generate_report_observation_vals(self, encounter=None, **kwargs):
        concept = self.concept_id or self
        return {
            "uom_id": concept.uom_id.id,
            "concept_id": self.concept_id.id,
            "name": self.name or self.concept_id.name,
            "reference_range_high": concept.reference_range_high,
            "reference_range_low": concept.reference_range_low,
            "display_type": self.display_type,
            "selection_options": concept.selection_options,
            "value_type": concept.value_type,
            "blocked": self.blocked or self.template_id.item_blocked,
            "sequence": self.sequence,
            "patient_id": encounter.patient_id.id,
        }

    @api.model
    def _get_reference_range_fields(self):
        return ["reference_range_low_view", "reference_range_high_view"]

    def _get_reference_range_values(self):
        return self.reference_range_low_view, self.reference_range_high_view
