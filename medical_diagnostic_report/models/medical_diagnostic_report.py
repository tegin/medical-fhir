# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MedicalDiagnosticReport(models.Model):

    _name = "medical.diagnostic.report"
    _inherit = ["medical.event", "medical.report.abstract", "digest.base"]
    _description = "Diagnostic Report"
    _rec_name = "internal_identifier"

    @api.model
    def _get_states(self):
        return {
            "registered": ("Registered", "draft"),
            "final": ("Final", "done"),
            "cancelled": ("Cancelled", "done"),
        }

    name = fields.Char(
        string="Report Name",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    fhir_state = fields.Selection(
        default="registered",
        copy=False,
        readonly=True,
    )
    lang = fields.Selection(string="Language", selection="_get_lang", readonly=True)
    # FHIR Field: status

    patient_id = fields.Many2one(
        "medical.patient",
        required=False,
        readonly=True,
    )
    patient_name = fields.Char(readonly=True, states={"draft": [("readonly", False)]})
    # FHIR Field: subject

    # FHIR Field: encounter

    vat = fields.Char(
        string="VAT", readonly=True, states={"draft": [("readonly", False)]}
    )

    patient_age = fields.Integer(readonly=True, states={"draft": [("readonly", False)]})

    patient_origin = fields.Char(readonly=True, states={"draft": [("readonly", False)]})

    issued_date = fields.Datetime(
        help="Date of report's publication",
        readonly=1,
        copy=False,
    )
    issued_user_id = fields.Many2one(
        "res.users", string="Issued by User", readonly=True, copy=False
    )
    # FHIR Field: Issued

    cancel_date = fields.Datetime(string="Cancelled Date", readonly=True, copy=False)
    cancel_user_id = fields.Many2one(
        "res.users", string="Cancelled by User", readonly=True, copy=False
    )
    conclusion = fields.Text(
        readonly=True,
        states={"draft": [("readonly", False)]},
        prefetch=False,
        compute="_compute_conclusion",
        inverse="_inverse_conclusion",
        copy=True,
    )
    database_conclusion = fields.Text(
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
        prefetch=False,
    )
    composition = fields.Html(
        readonly=True,
        states={"draft": [("readonly", False)]},
        compute="_compute_composition",
        inverse="_inverse_composition",
        prefetch=False,
        copy=True,
    )
    database_composition = fields.Html(
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
        prefetch=False,
    )
    observation_ids = fields.One2many(
        "medical.observation",
        inverse_name="diagnostic_report_id",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=True,
    )
    template_ids = fields.Many2many(
        "medical.diagnostic.report.template",
        relation="medical_diagnostic_report_templates_rel",
    )
    is_cancellable = fields.Boolean(compute="_compute_is_cancellable")
    duplicated_from_id = fields.Many2one(
        "medical.diagnostic.report",
        string="Duplicated From",
        readonly=True,
        copy=False,
    )

    @api.depends("database_composition")
    def _compute_composition(self):
        for record in self:
            record.composition = record._get_database_composition()

    def _inverse_composition(self):
        for record in self:
            record.database_composition = record.composition

    def _get_database_composition(self):
        return self.database_composition

    @api.depends("database_conclusion")
    def _compute_conclusion(self):
        for record in self:
            record.conclusion = record._get_database_conclusion()

    def _inverse_conclusion(self):
        for record in self:
            record.database_conclusion = record.conclusion

    def _get_database_conclusion(self):
        return self.database_conclusion

    @api.model
    def _get_lang(self):
        return self.env["res.lang"].get_installed()

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].sudo().next_by_code("medical.diagnostic.report")
            or "/"
        )

    def copy(self, default=None):
        default = dict(default or {})
        default.setdefault("duplicated_from_id", self.id)
        return super().copy(default=default)

    def _get_validate_on_behalf_user_id(self):
        return self.env.context.get("validate_on_behalf_user_id")

    def validate_on_behalf_action(self):
        self.ensure_one()
        if not self.performer_id:
            raise UserError(_("There is no performer set on this report."))
        user = self.env["res.users"].search(
            [("partner_id", "=", self.performer_id.id)], limit=1
        )
        if not user:
            raise UserError(
                _("There is no user linked to the performer %s.")
                % self.performer_id.display_name
            )
        self.with_context(validate_on_behalf_user_id=user.id).registered2final_action()

    def registered2final_change_state(self):
        return {
            "fhir_state": "final",
            "issued_date": fields.Datetime.now(),
            "issued_user_id": self._get_validate_on_behalf_user_id()
            or self.env.user.id,
        }

    def registered2final_action(self):
        self.ensure_one()
        self.write(self.registered2final_change_state())
        self.observation_ids.registered2final_action(
            observation_date=self._get_observation_date()
        )
        # The document is signed when issued.
        self._sign_document()
        signer_user_id = self._get_validate_on_behalf_user_id()
        if signer_user_id and signer_user_id != self.env.user.id:
            self.message_post(
                body=_(
                    "Report validated by %(actor)s on behalf of %(signer)s.",
                    actor=self.env.user.display_name,
                    signer=self.env["res.users"].browse(signer_user_id).display_name,
                )
            )

    def _get_observation_date(self):
        return fields.Datetime.now()

    def _cancel_vals(self):
        return {
            "fhir_state": "cancelled",
            "cancel_date": fields.Datetime.now(),
            "cancel_user_id": self.env.user.id,
        }

    def cancel_action(self):
        self.write(self._cancel_vals())
        self.observation_ids.cancel_action()

    @api.depends("fhir_state")
    def _compute_is_cancellable(self):
        for rec in self:
            rec.is_cancellable = rec._is_cancellable()

    def _is_cancellable(self):
        return self.fhir_state in ("registered", "final")

    def _generate_serializer(self):
        result = super(MedicalDiagnosticReport, self)._generate_serializer()
        result.update(
            {
                "name": self.name,
                "patient_id": self.patient_id.id,
                "patient_name": self.patient_name,
                "vat": self.vat,
                "patient_age": self.patient_age,
                "patient_origin": self.patient_origin,
                "issued_date": self.issued_date.isoformat(),
                "issued_user_id": self.issued_user_id.id,
                "conclusion": self.conclusion,
                "composition": self.composition,
                "observation_ids": [
                    obs._generate_serializer() for obs in self.observation_ids
                ],
            }
        )
        return result

    def preview_medical_diagnostic_report(self):
        return self.env.ref(
            "medical_diagnostic_report.medical_diagnostic_report"
        ).report_action(self)

    def open_document(self):
        self.ensure_one()
        url = (
            "/report/pdf/medical_diagnostic_report."
            + f"medical_diagnostic_report_template/{self.id}"
        )
        return {
            "isPdf": True,
            "isImage": False,
            "isText": False,
            "isVideo": False,
            "url": f"/web/static/lib/pdfjs/web/viewer.html?file={url}#pagemode=none",
            "isViewable": True,
            "defaultSource": url,
        }
