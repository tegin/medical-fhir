# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalReportAbstract(models.AbstractModel):

    _name = "medical.report.abstract"
    _description = "Abstract Diagnostic Report"

    name = fields.Char(string="Report name")
    medical_department = fields.Html(string="Medical Department")
    conclusion = fields.Text(string="Conclusions")
    composition = fields.Html(string="Composition")
    item_blocked = fields.Boolean(
        string="Item blocked", help="When checked, no lines can be added"
    )
    with_conclusion = fields.Boolean(
        string="With conclusion",
        help="When checked,a conclusion will be added",
    )
    with_composition = fields.Boolean(
        string="With composition",
        help="When checked,a composition will be added",
    )
    with_observation = fields.Boolean(
        string="With observations",
        help="When checked,a observation will be added",
    )


class MedicalReportItemAbstract(models.AbstractModel):

    _name = "medical.report.item.abstract"
    _description = "Abstract Diagnostic Report Item"

    name = fields.Text(string="Name", required=True)

    uom_id = fields.Many2one(
        "medical.observation.uom", string="Unit of measure"
    )

    uom_symbol = fields.Char(related="uom_id.symbol")

    reference_range_high = fields.Float()
    reference_range_low = fields.Float()
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

    def _get_reference_format(self):
        return self.uom_id.reference_format

    @api.depends(
        "reference_range_low", "reference_range_high",
    )
    def _compute_reference_range(self):
        for rec in self:
            range_limit = ""
            reference_format = rec._get_reference_format()
            if reference_format and (
                rec.reference_range_high or rec.reference_range_low
            ):
                range_limit = reference_format % (
                    rec.reference_range_low,
                    rec.reference_range_high,
                )
            rec.reference_range_limit = range_limit
