# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalObservation(models.Model):

    _name = "medical.observation"
    _inherit = "medical.report.item.abstract"
    _description = "Medical observation"
    _order = "observation_date desc, sequence, id"

    diagnostic_report_id = fields.Many2one(
        comodel_name="medical.diagnostic.report"
    )
    vat = fields.Char(related="diagnostic_report_id.vat", store=True)
    encounter_id = fields.Many2one(
        related="diagnostic_report_id.encounter_id", store=True
    )
    patient_id = fields.Many2one(
        "medical.patient", readonly=True, required=True
    )
    value = fields.Char(store=False)
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
        compute="_compute_interpretation",
        store=True,
    )
    # FHIR Field: interpretation
    observation_date = fields.Datetime(string="Date",)
    state = fields.Selection(
        [
            ("registered", "Registered"),
            ("final", "Final"),
            ("cancelled", "Cancelled"),
        ],
        default="registered",
        required=True,
        readonly=True,
    )  # TODO: We need a migration script to fix this

    value_representation = fields.Char(compute="_compute_value_representation")

    def registered2final_action(self, observation_date=False):
        for obs in self:
            vals = obs._registered2final_vals(
                observation_date=observation_date
            )
            if obs.uom_id and not obs.uom:
                vals.update(
                    {
                        "uom": obs.uom_id.name,
                        "reference_format": obs.uom_id.reference_format,
                    }
                )
            obs.write(vals)
        return True

    def _registered2final_vals(self, observation_date=observation_date):
        return {
            "state": "final",
            "observation_date": observation_date or fields.Datetime.now(),
        }

    def cancel_action(self):
        self.write(self._cancel_vals())

    def _cancel_vals(self):
        return {"state": "cancelled"}

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

    def _compute_value_representation(self):
        for rec in self:
            if rec.value_type and hasattr(rec, "value_%s" % rec.value_type):
                value = getattr(rec, "value_%s" % rec.value_type)
                rec.value_representation = value

    def get_value(self):
        self.ensure_one()
        if self.value_type == "float":
            return self.value_float
        else:
            return self.value_int
