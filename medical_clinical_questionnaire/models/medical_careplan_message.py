# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalCareplanMessage(models.Model):
    _inherit = "medical.careplan.message"

    procedure_ids = fields.One2many(
        "medical.procedure", inverse_name="medical_careplan_message_id"
    )
    procedure_message = fields.Html(compute="_compute_procedure_message")

    questionnaire_response_ids = fields.One2many(
        "medical.questionnaire.response",
        inverse_name="medical_careplan_message_id",
    )
    questionnaire_message = fields.Html(
        compute="_compute_questionnaire_message"
    )

    @api.depends("procedure_ids")
    def _compute_procedure_message(self):
        IrQweb = self.env["ir.qweb"]
        for record in self:
            if not record.procedure_ids:
                record.procedure_message = False
            else:
                record.procedure_message = IrQweb.render(
                    "medical_clinical_questionnaire.medical_procedure_messages_template",
                    {"o": record},
                )

    @api.depends("questionnaire_response_ids")
    def _compute_questionnaire_message(self):
        IrQweb = self.env["ir.qweb"]
        for record in self:
            if not record.questionnaire_response_ids:
                record.questionnaire_message = False
            else:
                record.questionnaire_message = IrQweb.render(
                    "medical_clinical_questionnaire.medical_questionnaire_messages_template",
                    {"o": record},
                )
