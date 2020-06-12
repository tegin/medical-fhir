# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


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

    def _compute_allow_back(self):
        for record in self:
            record.allow_back = getattr(
                record, "state_previous_%s" % record.state, False
            ) and (record.procedure_item_ids or record.questionnaire_item_ids)

    def _get_careplan_message_kwargs(self):
        result = super()._get_careplan_message_kwargs()
        result["procedure_request_ids"] = (
            self.procedure_item_ids.filtered(lambda r: r.state.done)
            .mapped("procedure_request_id")
            .ids
        )
        # TODO: probablemente no es el sitio a procesar esto
        questionnaire_response_ids = self.process_questionnaire_items()
        result["questionnaire_response_ids"] = questionnaire_response_ids.ids
        return result

    def process_questionnaire_items(self):
        responses = self.env["medical.questionnaire.response"]
        for pr in self.questionnaire_item_ids.filtered(
            lambda r: r.state.done
        ).mapped("procedure_request_id"):
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

    def state_exit_start(self):
        if self.questionnaire_item_ids.filtered(lambda r: not r.state):
            raise ValidationError(_("All items must have a state set"))
        items = []
        cp = self.careplan_medical_id
        for rec in self.questionnaire_item_ids:
            if not rec.state.done:
                items += [(2, item.id) for item in rec.item_ids]
            elif (
                rec.state.done or rec.state.only_timing
            ) and not rec.item_ids:
                items += [
                    (
                        0,
                        0,
                        cp._action_add_message_element_questionnaire_item_vals(
                            rec.procedure_request_id, question, rec.id
                        ),
                    )
                    for question in rec.procedure_request_id.questionnaire_id.item_ids
                ]
        self.write(
            {"state": "final", "questionnaire_item_response_ids": items}
        )

    def state_previous_final(self):
        self.write({"state": "start"})

    def add_message(self):
        res = super().add_message()
        for item in self.procedure_item_ids:
            if item.state == self.env.ref(
                "medical_clinical_questionnaire.wizard_state_generate_next"
            ):
                item.procedure_request_id.generate_new_event()
            elif item.state.done:
                if item.procedure_request_id.state == "draft":
                    item.procedure_request_id.draft2active()
                item.procedure_request_id.active2completed()

        for item in self.questionnaire_item_ids:
            if item.state == self.env.ref(
                "medical_clinical_questionnaire.wizard_state_generate_next"
            ):
                item.procedure_request_id.generate_new_event()
            elif item.state.done:
                if item.procedure_request_id.state == "draft":
                    item.procedure_request_id.draft2active()
                item.procedure_request_id.active2completed()
        return res


class WizardAddMedicalMessageProcedure(models.TransientModel):
    _name = "wizard.add.medical.message.procedure"
    _description = "Procedure in medical message"

    wizard_id = fields.Many2one("wizard.add.medical.message")
    procedure_request_id = fields.Many2one(
        "medical.procedure.request", required=True, readonly=True
    )
    name = fields.Char(compute="_compute_name")
    state = fields.Many2one(
        "medical.careplan.medical.wizard.state",
        domain="[('id', 'in', possible_states)]",
        default=False,
    )
    possible_states = fields.Many2many(
        "medical.careplan.medical.wizard.state",
        relation="procedure_wizard_states",
    )

    expected_date = fields.Datetime(
        related="procedure_request_id.next_expected_date",
        string="Expected Date",
    )

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

    wizard_id = fields.Many2one("wizard.add.medical.message")
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
    state = fields.Many2one(
        "medical.careplan.medical.wizard.state",
        domain="[('id', 'in', possible_states)]",
        default=False,
    )
    possible_states = fields.Many2many(
        "medical.careplan.medical.wizard.state",
        relation="questionnaire_wizard_states",
    )

    item_ids = fields.One2many(
        "wizard.add.medical.message.questionnaire.item",
        inverse_name="wizard_questionnaire_id",
    )

    expected_date = fields.Datetime(
        related="procedure_request_id.next_expected_date",
        string="Expected Date",
    )

    @api.depends("procedure_request_id")
    def _compute_name(self):
        for record in self:
            record.name = (
                record.procedure_request_id.service_id.display_name
                or record.procedure_request_id.name
            )
