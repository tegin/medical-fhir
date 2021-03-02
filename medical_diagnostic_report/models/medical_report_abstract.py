# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalReportAbstract(models.AbstractModel):

    _name = "medical.report.abstract"
    _description = "Abstract Diagnostic Report"

    name = fields.Char(string="Report name")
    conclusion = fields.Text(string="Conclusions")


class MedicalReportItemAbstract(models.AbstractModel):

    _name = "medical.report.item.abstract"
    _description = "Abstract Diagnostic Report Item"

    name = fields.Text(string="Name", required=True)

    uom_id = fields.Many2one(
        "medical.observation.uom", string="Unit of measure"
    )

    uom_symbol = fields.Char(related="uom_id.symbol")
    reference_format = fields.Char(related="uom_id.reference_format")

    reference_range_high = fields.Float()
    reference_range_low = fields.Float()
    reference_range_limit = fields.Char(
        string="Reference Range", compute="_compute_reference_range"
    )
    selection_options = fields.Char()
    value_type = fields.Selection([
        ("str", "String"),
        ("float", "Float"),
        ("bool", "Boolean"),
        ("int", "Integer")
    ])
    # FHIR Field: referenceRange

    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")],
        default=False,
        help="Technical field for UX purpose.",
    )

    @api.depends(
        "reference_range_low", "reference_range_high", "reference_format"
    )
    def _compute_reference_range(self):
        for rec in self:
            range_limit = ""
            if rec.reference_format and (
                rec.reference_range_high or rec.reference_range_low
            ):
                range_limit = rec.reference_format % (
                    rec.reference_range_low,
                    rec.reference_range_high,
                )
            rec.reference_range_limit = range_limit
