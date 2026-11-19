# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalReport(models.Model):
    _inherit = "medical.report"

    encounter_id = fields.Many2one("medical.encounter")
