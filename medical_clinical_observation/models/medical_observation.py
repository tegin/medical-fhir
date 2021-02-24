# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalObservation(models.Model):

    _name = "medical.observation"
    _description = "Medical Observation"

    # TODO: Link con encounter o careplan?
    encounter_id = fields.Many2one("medical.encounter", required=False)
    observation_date = fields.Datetime()

    observation_code_id = fields.Many2one(
        "medical.observation.code", required=True
    )
    observation_uom_id = fields.Many2one(
        "medical.observation.uom", required=True
    )

    field_type = fields.Selection(related="observation_code_id.field_type")

    char_value = fields.Char()
    float_value = fields.Float()
    integer_value = fields.Integer()

    @api.multi
    def get_value(self):
        self.ensure_one()
        if self.field_type == "integer":
            return self.integer_value
        elif self.field_type == "float":
            return self.float_value
        elif self.field_type == "char":
            return self.char_value
        return False

    @api.model
    def create_observation_value(self, new_value, field_type):
        values = {}
        if field_type in ["integer", "float", "char"]:
            values.update({"%s_value" % field_type: new_value})
        return values

    @api.model
    def create(self, vals):
        if "observation_value" not in vals:
            raise ValidationError(
                _("observation_value must be present in vals_list")
            )
        observation_value = vals.pop("observation_value")
        field_type = (
            self.env["medical.observation.code"]
            .browse(vals["observation_code_id"])
            .field_type
        )
        value_dict = self.create_observation_value(
            observation_value, field_type
        )
        vals.update(value_dict)
        return super().create(vals)
