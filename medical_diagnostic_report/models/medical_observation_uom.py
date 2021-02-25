from odoo import _, api, fields, models


class MedicalObservationUom(models.Model):

    _name = "medical.observation.uom"
    _description = "Medical Observation Unity of Measure"

    name = fields.Char(string="Unit of measure")
    symbol = fields.Char(string="Symbol")

    reference_format = fields.Char(default="%.2f - %.2f")
