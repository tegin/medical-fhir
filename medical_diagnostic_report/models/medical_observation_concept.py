# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalObservationConcept(models.Model):
    _name = "medical.observation.concept"
    _description = "Medical Observation Concept"

    name = fields.Char(required=True, translate=True)
    value_type = fields.Selection(
        selection=lambda r: r.env["medical.report.item.abstract"]
        ._fields["value_type"]
        .selection,
    )
    selection_options = fields.Char(translate=True)
    uom_id = fields.Many2one("uom.uom", string="Unit of measure")
    reference_range_low = fields.Float()
    reference_range_high = fields.Float()

    _sql_constraints = [
        ("name_uniq", "UNIQUE (name)", "Concept name must be unique!"),
        (
            "check_reference_range",
            "CHECK(reference_range_low <= reference_range_high)",
            "Reference range low cannot be larger that reference range high",
        ),
    ]
