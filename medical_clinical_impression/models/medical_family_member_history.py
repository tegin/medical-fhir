# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalFamilyMemberHistory(models.Model):
    # FHIR Entity: Family Member History
    _name = "medical.family.member.history"
    _inherit = ["medical.abstract", "mail.thread", "mail.activity.mixin"]
    _description = "Medical Family Member History"

    name = fields.Char(compute="_compute_name")
    # FHIR: state

    active = fields.Boolean(default=True)
    unable_to_obtain = fields.Boolean()

    patient_id = fields.Many2one("medical.patient")
    # FHIR: patient

    family_member_name = fields.Char()
    # FHIR: name

    relationship = fields.Char(required=True)
    # FHIR: relationship

    sex = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
            ("unknown", "Unknown"),
        ]
    )

    age = fields.Char(string="Age/Born Date")
    # FHIR: age. Same as born.
    # FHIR: born
    # It is a char field to be able to put an approximate date, or a date range...

    deceased = fields.Boolean()
    deceased_age = fields.Char(string="Deceased Age/Date")
    # FHIR: deceased

    note = fields.Text()
    # FHIR: note

    @api.depends("patient_id")
    def _compute_name(self):
        self.name = "Family History of %s" % self.patient_id.name

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code(
                "medical.family.member.history"
            )
            or "/"
        )
