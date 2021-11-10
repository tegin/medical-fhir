# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models


class MedicalCondition(models.Model):
    # FHIR Entity: Condition (https://www.hl7.org/fhir/condition.html)
    _name = "medical.condition"
    _inherit = "medical.abstract"
    _description = "Conditions"

    name = fields.Char(compute="_compute_condition_name")

    patient_id = fields.Many2one(
        comodel_name="medical.patient", string="Subject", required=True
    )  # FHIR Field: Subject

    clinical_finding_id = fields.Many2one(
        comodel_name="medical.clinical.finding"
    )

    active = fields.Boolean(default=True)

    create_warning = fields.Boolean(
        compute="_compute_create_warning", store=True
    )

    is_allergy = fields.Boolean()

    allergy_category = fields.Selection(
        [
            ("food", "Food"),
            ("medication", "Medication"),
            ("environment", "Environment"),
            ("biologic", "Biologic"),
        ]
    )
    criticality = fields.Selection([("low", "Low"), ("high", "High")])
    allergy_id = fields.Many2one(comodel_name="medical.allergy.substance")
    allergy_reaction_id = fields.Many2one(
        comodel_name="medical.clinical.finding"
    )
    last_occurrence_date = fields.Date()
    color = fields.Integer(default=1)

    # TODO: Remove non-necessary fields

    @api.model
    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.condition") or "/"

    def _compute_condition_name(self):
        for rec in self:
            if rec.is_allergy:
                rec.name = _("Allergy to %s" % rec.allergy_id.name)
            else:
                rec.name = rec.clinical_finding_id.name

    _sql_constraints = [
        (
            "finding_uniq",
            "UNIQUE(patient_id, clinical_finding_id)",
            "This finding already exists for this patient !",
        )
    ]
    # TODO: fix

    @api.depends(
        "allergy_id.create_warning", "clinical_finding_id.create_warning"
    )
    def _compute_create_warning(self):
        if (
            self.allergy_id.create_warning
            or self.clinical_finding_id.create_warning
        ):
            self.create_warning = True
        else:
            self.create_warning = False
