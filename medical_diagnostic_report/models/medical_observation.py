from odoo import _, api, fields, models


class MedicalObservation(models.Model):

    _name = "medical.observation"
    _inherit = "medical.report.item.abstract"
    _description = "Medical observation"

    diagnostic_report_id = fields.Many2one(
        comodel_name="medical.diagnostic.report"
    )
    value = fields.Float(string="Value")
    # FHIR Field: value

    interpretation = fields.Char(
        string="Interpretation", compute="_compute_interpretation"
    )
    # FHIR Field: interpretation

    @api.depends("value", "reference_range_low", "reference_range_high")
    def _compute_interpretation(self):
        for rec in self:
            label = ""
            if rec.reference_range_high or rec.reference_range_low:
                if (
                    rec.reference_range_low
                    <= rec.value
                    <= rec.reference_range_high
                ):
                    label = "Normal"
                elif rec.value > rec.reference_range_high:
                    label = "High"
                elif rec.value < rec.reference_range_low:
                    label = "Low"
            rec.interpretation = label

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("registered",):
                rec.is_editable = True
            else:
                rec.is_editable = False
