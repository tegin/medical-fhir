# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalObservationConcept(models.Model):

    _name = "medical.observation.concept"
    _description = "Medical Observation Concept"

    name = fields.Char(required=True, translate=True)
    template_item_id = fields.Many2one(
        comodel_name="medical.report.item.abstract"
    )
    value_type = fields.Selection(
        [
            ("str", "String"),
            ("float", "Float"),
            ("bool", "Boolean"),
            ("int", "Integer"),
            ("selection", "Selection"),
        ],
        translate=False,
    )
    selection_options = fields.Char()
    uom_id = fields.Many2one(
        "uom.uom", string="Unit of measure", translate=False
    )
    reference_range_low = fields.Float(translate=False)
    reference_range_high = fields.Float(translate=False)

    _sql_constraints = [
        ("name_uniq", "UNIQUE (name)", "Concept name must be unique!")
    ]
