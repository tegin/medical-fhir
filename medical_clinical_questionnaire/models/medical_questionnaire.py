# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class MedicalQuestionnaire(models.Model):
    # FHIR Entity: Questionnaire (http://hl7.org/fhir/questionnaire.html)
    _name = "medical.questionnaire"
    _inherit = "medical.abstract"
    _description = "Medical Questionnaire"

    name = fields.Char(required=True)
    title = fields.Char()
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("retired", "Retired")],
        required=True,
        default="active",
        track_visibility="onchange",
    )
    description = fields.Text()
    item_ids = fields.One2many(
        "medical.questionnaire.item", inverse_name="questionnaire_id"
    )
    check_code = fields.Char()

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.questionnaire")
            or "/"
        )


class MedicalQuestionnaireItem(models.Model):
    # FHIR Entity: Questionnaire (http://hl7.org/fhir/questionnaire.html)
    _name = "medical.questionnaire.item"
    # TODO Debería ser item abstract tambien?
    _description = "Medical Questionnaire Item"
    _order = "sequence asc, id asc"

    def _get_questionnaire_item_type(self):
        return [
            ("boolean", "Boolean"),
            ("float", "Decimal"),
            ("integer", "Integer"),
            ("date", "Date"),
            ("char", "Single line text"),
            ("text", "Multi line Text"),
            ("html", "Complex text"),
            ("selection", "Choice"),
        ]

    sequence = fields.Integer(required=True, default=20)
    questionnaire_id = fields.Many2one("medical.questionnaire", required=True)
    name = fields.Char(required=True)
    technical_name = fields.Char()
    required = fields.Boolean(default=False)
    readonly = fields.Boolean(default=False)
    readonly_condition = fields.Char()
    question_type = fields.Selection(
        selection=lambda r: r._get_questionnaire_item_type(), required=True
    )
    selection_options = fields.Char()
    options = fields.Char()
    default_code = fields.Char()
    is_invisible = fields.Boolean(string="invisible", default=False)
    invisible_condition = fields.Char()
    destination_field = fields.Char(
        help="""
            Destination of the child written as field names separated by points
        """
    )

    is_medical_observation = fields.Boolean()
    medical_observation_code_id = fields.Many2one("medical.observation.code")

    @api.constrains("questionnaire_id", "technical_name")
    def _check_technical_name(self):
        for record in self:
            if record.technical_name and self.search(
                [
                    ("id", "!=", record.id),
                    ("questionnaire_id", "=", record.questionnaire_id.id),
                    ("technical_name", "=", record.technical_name),
                ]
            ):
                raise ValidationError(
                    _("Technical name %s must be unique")
                    % record.technical_name
                )

    def _generate_default_result(self, procedure):
        if self.default_code:
            return safe_eval(self.default_code, {"object": procedure})
        return False

    def _generate_question_vals(self, procedure, wizard_id=False):
        return {
            "wizard_questionnaire_id": wizard_id,
            "name": self.name,
            "required": self.required,
            "question_type": self.question_type,
            "options": self.options,
            "selection_options": self.selection_options,
            "result": self._generate_default_result(procedure),
            "questionnaire_item_id": self.id,
            "procedure_request_id": procedure.id,
        }

    def _generate_question(self, response):
        vals = self._generate_question_vals(response.procedure_request_id)
        vals.update({"questionnaire_response_id": response.id})
        return self.env["medical.questionnaire.response.item"].create(vals)

    def config_item(self):
        return {
            "target": "new",
            "res_model": self._name,
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [
                (
                    self.env.ref(
                        "medical_clinical_questionnaire."
                        "medical_questionnaire_item_config_form_view"
                    ).id,
                    "form",
                )
            ],
        }
