# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalClinicalImpression(models.Model):

    _name = "medical.clinical.impression"
    _inherit = ["medical.event", "mail.thread", "mail.activity.mixin"]
    _description = "Medical Clinical Impression"
    _conditions = "condition_ids"
    _order = "validation_date desc, id"
    _rec_name = "internal_identifier"

    @api.model
    def _get_states(self):
        return {
            "in_progress": ("In Progress", "draft"),
            "completed": ("Completed", "done"),
            "cancelled": ("Cancelled", "done"),
        }

    fhir_state = fields.Selection(default="in_progress")

    specialty_id = fields.Many2one(
        "medical.specialty",
        required=True,
    )
    # FHIR code: type of clinical assessment performed.
    # TODO: add domain, so a partner can only select between their specialities

    description = fields.Text(
        help="Context of the impression: Why/how the assessment was performed"
    )
    # FHIR: description

    encounter_id = fields.Many2one("medical.encounter", required=True)
    # FHIR: encounter

    patient_id = fields.Many2one(related="encounter_id.patient_id")
    # FHIR: patient

    validation_date = fields.Datetime()
    # FHIR: date

    validation_user_id = fields.Many2one(
        "res.users", string="Validated by", readonly=True, copy=False
    )

    cancellation_date = fields.Datetime()

    cancellation_user_id = fields.Many2one(
        "res.users", string="Cancelled by", readonly=True, copy=False
    )
    finding_ids = fields.Many2many(comodel_name="medical.clinical.finding")
    # FHIR: finding
    allergy_substance_ids = fields.Many2many(
        comodel_name="medical.allergy.substance",
    )
    condition_ids = fields.One2many(
        comodel_name="medical.condition",
        string="Conditions",
        related="patient_id.medical_condition_ids",
    )

    condition_count = fields.Integer(
        related="patient_id.medical_condition_count"
    )

    summary = fields.Text()
    # FHIR: summary
    note = fields.Text()
    # FHIR: Note

    current_encounter = fields.Boolean(
        help="This field is only used to stand out the impressions "
        "of the current encounter in the tree view",
        compute="_compute_current_encounter",
    )

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.clinical.impression")
            or "/"
        )

    @api.depends("encounter_id")
    def _compute_current_encounter(self):
        for rec in self:
            current_encounter = False
            if self.env.context.get("encounter_id"):
                default_encounter = self.env.context.get("encounter_id")
                if default_encounter == rec.encounter_id.id:
                    current_encounter = True
            rec.current_encounter = current_encounter

    def _create_conditions_from_findings(self):
        finding_ids = self.finding_ids.filtered(
            lambda f: f.create_condition_from_clinical_impression
        )
        if finding_ids:
            for finding in finding_ids:
                condition = self.patient_id.medical_condition_ids.filtered(
                    lambda r: r.clinical_finding_id.id == finding.id
                )
                if not condition:
                    self.env["medical.condition"].create(
                        {
                            "patient_id": self.patient_id.id,
                            "clinical_finding_id": finding.id,
                            "origin_clinical_impression_id": self.id,
                        }
                    )

    def _create_allergies_from_findings(self):
        if self.allergy_substance_ids:
            for substance in self.allergy_substance_ids:
                allergy = self.patient_id.medical_allergy_ids.filtered(
                    lambda r: r.allergy_id.id == substance.id
                )
                if not allergy:
                    self.env["medical.condition"].create(
                        {
                            "patient_id": self.patient_id.id,
                            "is_allergy": True,
                            "allergy_id": substance.id,
                            "origin_clinical_impression_id": self.id,
                        }
                    )

    def _validate_clinical_impression_fields(self):
        return {
            "fhir_state": "completed",
            "validation_date": fields.Datetime.now(),
            "validation_user_id": self.env.user.id,
        }

    def validate_clinical_impression(self):
        self.ensure_one()
        self.write(self._validate_clinical_impression_fields())
        self._create_conditions_from_findings()
        self._create_allergies_from_findings()

    def _cancel_clinical_impression_fields(self):
        return {
            "fhir_state": "cancelled",
            "cancellation_date": fields.Datetime.now(),
            "cancellation_user_id": self.env.user.id,
        }

    def _cancel_related_conditions(self):
        related_conditions = self.condition_ids.filtered(
            lambda r: r.origin_clinical_impression_id.id == self.id
        )
        related_conditions.active = False

    def cancel_clinical_impression(self):
        self.ensure_one()
        self._cancel_related_conditions()
        self.write(self._cancel_clinical_impression_fields())
