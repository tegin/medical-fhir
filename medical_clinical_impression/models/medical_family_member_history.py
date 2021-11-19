# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalFamilyMemberHistory(models.Model):
    # FHIR Entity: Family Member History
    _name = "medical.family.member.history"
    _inherit = "medical.abstract"
    _description = "Medical Family Member History"

    # FHIR: state
    active = fields.Boolean(default=True)
    unable_to_obtain = fields.Boolean()
    # FHIR: tdataAbstenReaso, in fact is a codeable concept
    # It could also be determined at the patient profile

    patient_id = fields.Many2one("medical.patient")
    # FHIR: patient

    recorded_date = fields.Date()
    # FHIR: date

    family_member_name = fields.Char()
    # FHIR: name

    relationship = fields.Char()
    # FHIR: relationship (in fact is a codeableConcept)

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

    condition_ids = fields.One2many(
        "medical.family.member.history.condition",
        inverse_name="family_history_id",
    )
    # FHIR: conditions. It should be a codeableconcept,
    # but maybe the patient does not know exactly. For.example: cancer

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


class MedicalFamilyMemberHistoryCondition(models.Model):

    _name = "medical.family.member.history.condition"
    _description = "Medical Family Member History Condition"

    name = fields.Char()

    contributed_to_death = fields.Boolean()

    family_history_id = fields.Many2one("medical.family.member.history")

    note = fields.Text()
