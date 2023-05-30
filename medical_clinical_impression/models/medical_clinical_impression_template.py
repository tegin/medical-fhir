# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalClinicalImpressionTemplate(models.Model):

    _name = "medical.clinical.impression.template"
    _description = "Medical Clinical Impression Template"  # TODO

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    specialty_id = fields.Many2one(
        "medical.specialty",
        required=False,
        domain="[('specialty_id', '=', specialty_id)]",
    )
