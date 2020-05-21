# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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

    @api.constrains("procedure_request_id")
    def _check_procedure(self):
        if self.env.context.get("force_one_procedure", False):
            super()._check_procedure()
