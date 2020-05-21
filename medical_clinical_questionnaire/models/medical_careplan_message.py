# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalCareplanMessage(models.Model):
    _inherit = "medical.careplan.message"

    procedure_ids = fields.One2many(
        "medical.procedure", inverse_name="medical_careplan_message_id"
    )
    procedure_message = fields.Html(compute="_compute_procedure_message")

    @api.depends("procedure_ids")
    def _compute_procedure_message(self):
        IrQweb = self.env["ir.qweb"]
        for record in self:
            if not record.procedure_ids:
                record.procedure_message = False
                continue
            record.procedure_message = IrQweb.render(
                "medical_clinical_questionnaire.medical_procedure_messages_template",
                {"o": record},
            )
