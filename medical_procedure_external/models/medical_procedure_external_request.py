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
        return [
            ("draft", "Draft"),
            ("final", "Final"),
            ("cancelled", "Cancelled"),
        ]

    name = fields.Char(string="Procedure Name")
    state = fields.Selection(
        default="draft",
        copy=False,
    )
    lang = fields.Selection(
        string="Language", selection="_get_lang", readonly=True
    )
    patient_id = fields.Many2one(
        related="encounter_id.patient_id",
        store=True,
        required=False,
        readonly=True,
    )
    patient_name = fields.Char()
    encounter_id = fields.Many2one("medical.encounter", readonly=True)
    vat = fields.Char(string="VAT", readonly=True)
    patient_age = fields.Integer(readonly=True)
    patient_origin = fields.Char(
        readonly=True,
    )
    issued_date = fields.Datetime(
        help="Date of report's publication",
        readonly=True,
        copy=False,
    )
    issued_user_id = fields.Many2one(
        "res.users", string="Issued by User", readonly=True, copy=False
    )
    composition = fields.Html(readonly=True)
    is_cancellable = fields.Boolean(compute="_compute_is_cancellable")
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
            "state": "final",
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
            "state": "cancelled",
            "cancel_date": fields.Datetime.now(),
            "cancel_user_id": self.env.user.id,
        }

    def cancel_action(self):
        self.write(self._cancel_vals())

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            rec.is_editable = rec._is_editable()

    def _is_editable(self):
        return self.state in ("draft",)

    @api.depends("state")
    def _compute_is_cancellable(self):
        for rec in self:
            rec.is_cancellable = rec._is_cancellable()

    def _is_cancellable(self):
        return self.state in ("draft", "final")
