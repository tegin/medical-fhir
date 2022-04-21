# Copyright 2022 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalCondition(models.Model):

    _name = "medical.condition"
    _inherit = "medical.condition"

    origin_clinical_impression_id = fields.Many2one(
        comodel_name="medical.clinical.impression"
    )
