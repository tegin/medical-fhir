# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalFamilyMemberHistory(models.Model):
    # FHIR Entity: Family Member History
    _name = "medical.family.member.history"
    _inherit = "medical.abstract"
    _description = "Medical Family Member History"

    name = fields.Char(compute="_compute_name")
    # FHIR: state

    def _compute_name(self):
        self.name = "Familiar History of %s" % self.patient_id.name

    active = fields.Boolean(default=True)
    unable_to_obtain = fields.Boolean()

    patient_id = fields.Many2one("medical.patient")
    # FHIR: patient

    family_member_name = fields.Char()
    # FHIR: name

    relationship = fields.Char()
    # FHIR: relationship

    sex = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
            ("unknown", "Unknown"),
        ]
    )

    born_date = fields.Char()
    # FHIR: born . This is given bu char becasue in
    # this way it can put an approximate date, or a date range...

    age = fields.Char()
    # FHIR: age. Same as born.

    deceased = fields.Boolean()
    deceased_date = fields.Char()
    deceased_age = fields.Char()
    # FHIR: deceased

    note = fields.Text()
    # FHIR: note

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code(
                "medical.family.member.history"
            )
            or "/"
        )
