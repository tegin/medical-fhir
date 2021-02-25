# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MedicalDiagnosticReport(models.Model):

    _name = "medical.diagnostic.report"
    _inherit = ["medical.event", "medical.report.abstract"]
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
    # FHIR Field: status

    patient_id = fields.Many2one(
        related="encounter_id.patient_id",
        store=True,
        required=False,
        readonly=True,
    )
    # FHIR Field: subject

    encounter_id = fields.Many2one("medical.encounter", readonly=True)
    # FHIR Field: encounter

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
    observation_ids = fields.One2many(
        "medical.observation", inverse_name="diagnostic_report_id", copy=True
    )

    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.diagnostic.report")
            or "/"
        )

    def registered2final_change_state(self):
        return {"state": "final"}

    def registered2final_action(self):
        self.write(self.registered2final_change_state())
        self.issued_date = fields.Datetime.now()
        self.issued_user_id = self.env.user

    def final2cancelled_change_state(self):
        return {"state": "cancelled"}

    def final2cancelled_action(self):
        self.write(self.final2cancelled_change_state())
        self.cancel_date = fields.Datetime.now()
        self.cancel_user_id = self.env.user

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            if rec.state in ("registered",):
                rec.is_editable = True
            else:
                rec.is_editable = False
