# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

FIELD_TYPE_SELECTION = [
    ("integer", "Integer"),
    ("float", "Float"),
    ("char", "Text"),
    ("selection", "Selection"),
]


class MedicalObservationCode(models.Model):

    _name = "medical.observation.code"
    _description = "Medical Observation Code"

    name = fields.Char(required=True)
    # color = fields.Char(string="Chart Color", default="#0000ff")

    integration_code = fields.Integer()

    possible_observation_uom_ids = fields.Many2many(
        "medical.observation.uom", string="Possible Unities of Measure"
    )
    default_observation_uom = fields.Many2one(
        "medical.observation.uom",
        string="Default Unity of Measure",
        domain="[('id', 'in', possible_observation_uom_ids)]",
    )

    field_type = fields.Selection(
        selection=FIELD_TYPE_SELECTION, required=True
    )

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Measure already exists!"),
        (
            "integration_code_uniq",
            "unique (integration_code)",
            "Measure already exists!",
        ),
    ]
