# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalCoverage(models.Model):
    # FHIR Entity: Coverage (https://www.hl7.org/fhir/coverage.html)
    _name = "medical.coverage"
    _description = "Medical Coverage"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Name",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    patient_id = fields.Many2one(
        string="Patient",
        comodel_name="medical.patient",
        required=True,
        ondelete="restrict",
        index=True,
        tracking=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Patient name",
    )  # FHIR Field: beneficiary
    coverage_template_id = fields.Many2one(
        string="Coverage Template",
        comodel_name="medical.coverage.template",
        required=True,
        ondelete="restrict",
        index=True,
        help="Coverage Template",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        string="Coverage Status",
        required="True",
        selection=[
            ("draft", "Draft"),
            ("active", "Active"),
            ("cancelled", "Cancelled"),
            ("entered-in-error", "Entered In Error"),
        ],
        default="draft",
        tracking=True,
        help="Current state of the coverage.",
    )  # FHIR Field: status
    subscriber_id = fields.Char(
        string="Subscriber Id",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].sudo().next_by_code("medical.coverage")
            or "/"
        )

    @api.depends("name", "internal_identifier")
    def name_get(self):
        result = []
        for record in self:
            name = "[%s]" % record.internal_identifier
            if record.name:
                name = "{} {}".format(name, record.name)
            result.append((record.id, name))
        return result

    def draft2active(self):
        self.write({"state": "active"})

    def draft2cancelled(self):
        self.write({"state": "cancelled"})

    def draft2enteredinerror(self):
        self.write({"state": "entered-in-error"})

    def active2cancelled(self):
        self.write({"state": "cancelled"})

    def active2enteredinerror(self):
        self.write({"state": "entered-in-error"})

    def cancelled2enteredinerror(self):
        self.write({"state": "entered-in-error"})

    def active2draft(self):
        self.write({"state": "draft"})

    def cancelled2draft(self):
        self.write({"state": "draft"})

    def cancelled2active(self):
        self.write({"state": "active"})
