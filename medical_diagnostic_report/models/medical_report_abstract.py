# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalReportAbstract(models.AbstractModel):

    _name = "medical.report.abstract"
    _description = "Abstract Diagnostic Report"

    name = fields.Char(string="Report Name")
    conclusion = fields.Text()
    composition = fields.Html()
    item_blocked = fields.Boolean(help="When checked, no lines can be added")
    with_conclusion = fields.Boolean(
        help="When checked,a conclusion will be added",
    )
    with_composition = fields.Boolean(
        help="When checked,a composition will be added",
    )
    with_observation = fields.Boolean(
        string="With observations",
        help="When checked,a observation will be added",
    )


class MedicalReportItemAbstract(models.AbstractModel):

    _name = "medical.report.item.abstract"
    _description = "Abstract Diagnostic Report Item"

    sequence = fields.Integer(default=20)

    concept_id = fields.Many2one(comodel_name="medical.observation.concept")
    name = fields.Char()
    uom_id = fields.Many2one("uom.uom", string="Unit of measure")

    reference_range_low = fields.Float()
    reference_range_high = fields.Float()

    reference_range_limit = fields.Char(
        string="Reference Range", compute="_compute_reference_range"
    )
    # FHIR Field: referenceRange
    selection_options = fields.Char()
    value_type = fields.Selection(
        [
            ("str", "String"),
            ("float", "Float"),
            ("bool", "Boolean"),
            ("int", "Integer"),
            ("selection", "Selection"),
        ]
    )
    blocked = fields.Boolean()

    display_type = fields.Selection(
        [
            ("line_section", "Section"),
            ("line_note", "Note"),
            ("line_subsection", "Subsection"),
        ],
        default=False,
        help="Technical field for UX purpose.",
    )

    @api.onchange("concept_id")
    def _onchange_observation_concept(self):
        if self.concept_id:
            self.name = self.concept_id.name
            self.value_type = self.concept_id.value_type
            self.uom_id = self.concept_id.uom_id
            self.reference_range_low = self.concept_id.reference_range_low
            self.reference_range_high = self.concept_id.reference_range_high
        return {}

    def _get_reference_format(self):
        return self.uom_id.reference_format

    def _get_lang(self):
        return self.env.context.get("lang") or "en_US"

    @api.depends(
        "reference_range_low", "reference_range_high",
    )
    def _compute_reference_range(self):
        for rec in self:
            range_limit = ""
            reference_format = rec._get_reference_format()
            lang_code = rec._get_lang()
            lang = self.env["res.lang"]._lang_get(lang_code)
            if reference_format and (
                rec.reference_range_high or rec.reference_range_low
            ):
                range_limit = "{} - {}".format(
                    lang.format(
                        reference_format,
                        rec.reference_range_low or 0,
                        grouping=True,
                    ),
                    lang.format(
                        reference_format,
                        rec.reference_range_high or 0,
                        grouping=True,
                    ),
                )
            rec.reference_range_limit = range_limit
