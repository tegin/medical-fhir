# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalObservationUom(models.Model):

    _name = "medical.observation.uom"
    _description = "Medical Observation Uom"

    name = fields.Char()
    symbol = fields.Char()
    # integration_code = fields.Integer(required=True)
