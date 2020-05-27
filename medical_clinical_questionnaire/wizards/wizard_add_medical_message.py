# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class WizardAddMedicalMessage(models.TransientModel):

    _inherit = "wizard.add.medical.message"

    procedure_item_ids = fields.One2many(
        "wizard.add.medical.message.procedure", inverse_name="wizard_id"
    )

    questionnaire_item_ids = fields.One2many(
        "wizard.add.medical.message.questionnaire", inverse_name="wizard_id"
    )

    questionnaire_item_response_ids = fields.One2many(
        "wizard.add.medical.message.questionnaire.item",
        inverse_name="wizard_id",
    )

    @api.onchange("questionnaire_item_ids")
    def onchange_done(self):
        items = []
        for rec in self.questionnaire_item_ids:
            if not rec.done:
                continue
            items += [
                (
                    0,
                    0,
                    self.careplan_medical_id._action_add_message_element_questionnaire_item_vals(
                        rec.procedure_request_id, question
                    ),
                )
                for question in rec.procedure_request_id.questionnaire_id.item_ids
            ]
        self.questionnaire_item_response_ids = items

    def _get_careplan_message_kwargs(self):
        result = super()._get_careplan_message_kwargs()
        result["procedure_request_ids"] = (
            self.procedure_item_ids.filtered(lambda r: r.done)
            .mapped("procedure_request_id")
            .ids
        )
        # TODO: probablemente no es el sitio a procesar esto
        questionnaire_response_ids = self.process_questionnaire_items()
        result["questionnaire_response_ids"] = questionnaire_response_ids.ids
        return result

    def process_questionnaire_items(self):
        responses = self.env["medical.questionnaire.response"]
        for pr in self.questionnaire_item_ids.mapped("procedure_request_id"):
            vals = []
            for item in self.questionnaire_item_response_ids:
                if item.procedure_request_id.id == pr.id:
                    item_vals = {
                        "result": item.result,
                        "questionnaire_item_id": item.questionnaire_item_id.id,
                    }
                    vals.append((0, 0, item_vals))
            responses |= self.env["medical.questionnaire.response"].create(
                {
                    "medical_careplan_id": self.careplan_medical_id.id,
                    "procedure_request_id": pr.id,
                    "item_ids": vals,
                    "state": "completed",
                    "questionnaire_id": pr.questionnaire_id.id,
                    "patient_id": self.careplan_medical_id.patient_id.id,
                }
            )
        return responses

    def add_message(self):
        res = super().add_message()
        return res


class WizardAddMedicalMessageProcedure(models.TransientModel):
    _name = "wizard.add.medical.message.procedure"
    _description = "Procedure in medical message"

    wizard_id = fields.Many2one("wizard.add.medical.message")
    procedure_request_id = fields.Many2one(
        "medical.procedure.request", required=True, readonly=True
    )
    name = fields.Char(compute="_compute_name")
    done = fields.Boolean()

    @api.depends("procedure_request_id")
    def _compute_name(self):
        for record in self:
            record.name = (
                record.procedure_request_id.service_id.display_name
                or record.procedure_request_id.name
            )


class WizardAddMedicalMessageQuestionnaireItem(models.TransientModel):
    _name = "wizard.add.medical.message.questionnaire.item"
    _inherit = "medical.questionnaire.item.abstract"
    _description = "Questionnaire in medical message"

    wizard_id = fields.Many2one("wizard.add.medical.message",)
    wizard_questionnaire_id = fields.Many2one(
        "wizard.add.medical.message.questionnaire"
    )


class WizardAddMedicalMessageQuestionnaire(models.TransientModel):
    _name = "wizard.add.medical.message.questionnaire"
    _description = "Questionnaire in medical message"

    wizard_id = fields.Many2one("wizard.add.medical.message")
    procedure_request_id = fields.Many2one(
        "medical.procedure.request", required=True, readonly=True
    )
    name = fields.Char(compute="_compute_name")
    done = fields.Boolean()
    item_ids = fields.One2many(
        "wizard.add.medical.message.questionnaire.item",
        inverse_name="wizard_questionnaire_id",
    )

    @api.depends("procedure_request_id")
    def _compute_name(self):
        for record in self:
            record.name = (
                record.procedure_request_id.service_id.display_name
                or record.procedure_request_id.name
            )
