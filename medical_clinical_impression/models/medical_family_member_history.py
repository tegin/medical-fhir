# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from datetime import date

from dateutil.relativedelta import relativedelta

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

    born_date = fields.Date()
    age = fields.Integer(compute="_compute_age")
    # FHIR: age. Same as born.
    # FHIR: born
    # It is a char field to be able to put an approximate date, or a date range...

    deceased = fields.Boolean()
    deceased_date = fields.Date()
    deceased_age = fields.Integer(compute="_compute_deceased_age")
    # FHIR: deceased

    note = fields.Text()
    # FHIR: note

    @api.depends("patient_id")
    def _compute_name(self):
        self.name = "Family History of %s" % self.patient_id.name

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.family.member.history") or "/"
        )

    @api.depends("born_date")
    def _compute_age(self):
        for record in self:
            if record.born_date:
                record.age = relativedelta(date.today(), record.born_date).years
            else:
                record.age = 0

    @api.depends("deceased_date", "born_date")
    def _compute_deceased_age(self):
        for record in self:
            if record.deceased_date and record.born_date:
                record.deceased_age = relativedelta(
                    record.deceased_date, record.born_date
                ).years
            else:
                record.deceased_age = 0
