# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalObservation(models.Model):

    _name = "medical.observation"
    _inherit = "medical.report.item.abstract"
    _description = "Medical observation"

    diagnostic_report_id = fields.Many2one(
        comodel_name="medical.diagnostic.report"
    )
    value = fields.Char(string="Value", store=False)
    value_float = fields.Float()
    value_str = fields.Char()
    value_selection = fields.Char()
    value_int = fields.Integer()
    value_bool = fields.Boolean()
    # FHIR Field: value
    uom = fields.Char(readonly=True)
    reference_format = fields.Char(readonly=True)
    interpretation = fields.Selection(
        [("low", "Low"), ("normal", "Normal"), ("high", "High")],
        string="Interpretation",
        compute="_compute_interpretation",
    )
    # FHIR Field: interpretation

    @api.depends(
        "value_float",
        "value_int",
        "reference_range_low",
        "reference_range_high",
    )
    def _compute_interpretation(self):
        for rec in self:
            label = False
            if rec.reference_range_high or rec.reference_range_low:
                if rec.value_float:
                    if rec.value_float > rec.reference_range_high:
                        label = "high"
                    elif rec.value_float < rec.reference_range_low:
                        label = "low"
                    else:
                        label = "normal"

                elif rec.value_int:

                    if rec.value_int > rec.reference_range_high:
                        label = "high"
                    elif rec.value_int < rec.reference_range_low:
                        label = "low"
                    else:
                        label = "normal"
            rec.interpretation = label

    def _get_reference_format(self):
        return (
            self.reference_format
            or super(MedicalObservation, self)._get_reference_format()
        )

    def _generate_serializer(self):
        value = False
        if self.value_type and hasattr(self, "value_%s" % self.value_type):
            value = getattr(self, "value_%s" % self.value_type)
        return {
            "id": self.id,
            "value": value,
            "name": self.name,
            "uom": self.uom,
            "reference_range_low": self.reference_range_low,
            "reference_range_high": self.reference_range_high,
            "interpretation": self.interpretation,
        }
