# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalDiagnosticReport(models.Model):

    _name = "medical.diagnostic.report"
    _inherit = ["medical.event", "medical.report.abstract", "digest.base"]
    _description = "Diagnostic Report"
    _rec_name = "internal_identifier"

    @api.model
    def _get_states(self):
        return [
            ("registered", "Registered"),
            ("final", "Final"),
            ("cancelled", "Cancelled"),
        ]

    name = fields.Char(string="Report Name")
    state = fields.Selection(default="registered", copy=False,)
    lang = fields.Selection(
        string="Language", selection="_get_lang", readonly=True
    )
    # FHIR Field: status

    patient_id = fields.Many2one(
        related="encounter_id.patient_id",
        store=True,
        required=False,
        readonly=True,
    )
    patient_name = fields.Char()
    # FHIR Field: subject

    encounter_id = fields.Many2one("medical.encounter", readonly=True)
    # FHIR Field: encounter

    vat = fields.Char(string="VAT", readonly=True)

    patient_age = fields.Integer(readonly=True)

    patient_origin = fields.Char(readonly=True,)

    issued_date = fields.Datetime(
        help="Date of report's publication", readonly=0, copy=False,
    )
    issued_user_id = fields.Many2one(
        "res.users", string="Issued by User", readonly=True, copy=False
    )
    # FHIR Field: Issued

    cancel_date = fields.Datetime(
        string="Cancelled Date", readonly=True, copy=False
    )
    cancel_user_id = fields.Many2one(
        "res.users", string="Cancelled by User", readonly=True, copy=False
    )

    conclusion = fields.Text(readonly=True)
    composition = fields.Html(readonly=True)
    observation_ids = fields.One2many(
        "medical.observation", inverse_name="diagnostic_report_id", copy=True
    )
    template_ids = fields.Many2many(
        "medical.diagnostic.report.template",
        relation="medical_diagnostic_report_templates_rel",
    )
    is_cancellable = fields.Boolean(compute="_compute_is_cancellable")

    @api.model
    def _get_lang(self):
        return self.env["res.lang"].get_installed()

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.diagnostic.report")
            or "/"
        )

    def registered2final_change_state(self):
        return {
            "state": "final",
            "issued_date": fields.Datetime.now(),
            "issued_user_id": self.env.user.id,
        }

    def registered2final_action(self):
        self.ensure_one()
        self.write(self.registered2final_change_state())
        self.observation_ids.registered2final_action(
            observation_date=self._get_observation_date()
        )
        # The document is signed when issued.
        self._sign_document()

    def _get_observation_date(self):
        return self.encounter_id.create_date

    def _cancel_vals(self):
        return {
            "state": "cancelled",
            "cancel_date": fields.Datetime.now(),
            "cancel_user_id": self.env.user.id,
        }

    def cancel_action(self):
        self.write(self._cancel_vals())
        self.observation_ids.cancel_action()

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            rec.is_editable = rec._is_editable()

    def _is_editable(self):
        return self.state in ("registered",)

    @api.depends("state")
    def _compute_is_cancellable(self):
        for rec in self:
            rec.is_cancellable = rec._is_cancellable()

    def _is_cancellable(self):
        return self.state in ("registered", "final")

    def _generate_serializer(self):
        result = super(MedicalDiagnosticReport, self)._generate_serializer()
        result.update(
            {
                "name": self.name,
                "patient_id": self.patient_id.id,
                "patient_name": self.patient_name,
                "encounter_id": self.encounter_id.id,
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
