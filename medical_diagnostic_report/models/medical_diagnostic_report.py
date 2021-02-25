# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalDiagnosticReport(models.Model):

    _name = "medical.diagnostic.report"
    _inherit = ["medical.event", "medical.report.abstract", "digest.base"]
    _description = "Diagnostic Report"
    _rec_name = "internal_identifier"

    name = fields.Char(string="Report name")
    state = fields.Selection(
        [
            ("registered", "Registered"),
            ("final", "Final"),
            ("cancelled", "Cancelled"),
        ],
        default="registered",
        copy=False,
    )
    medical_department = fields.Html(readonly=True)
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

    patient_age = fields.Integer(string="Patient Age", readonly=True)

    patient_origin = fields.Char(string="Patient Origin", readonly=True,)

    issued_date = fields.Datetime(
        string="Issued Date",
        help="Date of report's publication",
        readonly=True,
        copy=False,
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
        for obs in self.observation_ids:
            if obs.uom_id and not obs.uom:
                obs.write(
                    {
                        "uom": obs.uom_id.name,
                        "reference_format": obs.uom_id.reference_format,
                    }
                )
        # The document is signed when issued.
        self._sign_document()

    def final2cancelled_change_state(self):
        return {
            "state": "cancelled",
            "cancel_date": fields.Datetime.now(),
            "cancel_user_id": self.env.user.id,
        }

    def final2cancelled_action(self):
        self.write(self.final2cancelled_change_state())

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            rec.is_editable = rec.state in ("registered",)

    def _generate_serializer(self):
        result = super(MedicalDiagnosticReport, self)._generate_serializer()
        result.update(
            {
                "name": self.name,
                "patient_id": self.patient_id.id,
                "patient_name": self.patient_name,
                "encounter_id": self.encounter_id.id,
                "vat": self.vat,
                "medical_department": self.medical_department,
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
