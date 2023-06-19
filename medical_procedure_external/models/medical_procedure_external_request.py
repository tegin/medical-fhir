# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalProcedureExternalRequest(models.Model):
    _name = "medical.procedure.external.request"
    _inherit = ["medical.event", "digest.base"]
    _description = "Procedure external"
    _rec_name = "internal_identifier"

    @api.model
    def _get_states(self):
        return {
            "draft": ("Draft", "draft"),
            "final": ("Final", "done"),
            "cancelled": ("Cancelled", "done"),
        }

    name = fields.Char(
        string="Procedure Name",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    fhir_state = fields.Selection(
        default="draft",
        copy=False,
    )
    lang = fields.Selection(
        string="Language",
        selection="_get_lang",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    patient_id = fields.Many2one(
        related="encounter_id.patient_id",
        store=True,
        required=False,
        readonly=True,
    )
    patient_name = fields.Char(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    encounter_id = fields.Many2one(
        "medical.encounter",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    vat = fields.Char(
        string="VAT", readonly=True, states={"draft": [("readonly", False)]}
    )
    patient_age = fields.Integer(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    patient_origin = fields.Char(
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    issued_date = fields.Datetime(
        help="Date of report's publication",
        readonly=True,
        copy=False,
    )
    issued_user_id = fields.Many2one(
        "res.users", string="Issued by User", readonly=True, copy=False
    )
    composition = fields.Html(
        readonly=True, states={"draft": [("readonly", False)]}
    )
    cancel_date = fields.Datetime(
        string="Cancelled Date", readonly=True, copy=False
    )
    cancel_user_id = fields.Many2one(
        "res.users", string="Cancelled by User", readonly=True, copy=False
    )
    template_ids = fields.Many2many(
        "medical.procedure.external.request.template",
        relation="medical_procedure_external_request_templates_rel",
    )

    @api.model
    def _get_lang(self):
        return self.env["res.lang"].get_installed()

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code(
                "medical.procedure.external.request"
            )
            or "/"
        )

    def draft2final_change_state(self):
        return {
            "fhir_state": "final",
            "issued_date": fields.Datetime.now(),
            "issued_user_id": self.env.user.id,
        }

    def draft2final_action(self):
        self.ensure_one()
        self.write(self.draft2final_change_state())
        # The document is signed when issued.
        self._sign_document()

    def _cancel_vals(self):
        return {
            "fhir_state": "cancelled",
            "cancel_date": fields.Datetime.now(),
            "cancel_user_id": self.env.user.id,
        }

    def cancel_action(self):
        self.write(self._cancel_vals())
