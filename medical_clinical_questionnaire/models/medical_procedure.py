# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalProcedure(models.Model):

    _inherit = "medical.procedure"

    medical_careplan_message_id = fields.Many2one(
        "medical.careplan.message", readonly=True
    )
    medical_careplan_id = fields.Many2one(
        "medical.careplan.medical",
        related="medical_careplan_message_id.medical_careplan_id",
        store=True,
    )
