# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MedicalClinicalImpression(models.Model):

    _name = "medical.clinical.impression"
    _inherit = "medical.event"
    _description = "Medical Clinical Impression"
    _conditions = "condition_ids"

    @api.model
    def _get_states(self):
        return [
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ]

    name = fields.Char(compute="_compute_clinical_impression_name", copy=False)

    state = fields.Selection(default="in_progress", states={}, required=False)
    #   FHIR: status

    @api.model
    def _get_impression_specialty_id(self):
        if self.create_uid.partner_id.specialty_ids:
            return self.create_uid.partner_id.specialty_ids[0].name
        else:
            return False

    specialty_id = fields.Many2one(
        "medical.specialty",
        default=_get_impression_specialty_id,
        required=True,
    )
    # FHIR code: type of clinical assessment performed.
    # Can be used as a tag. Which should be related model?
    # Related to the specialty?
    # It can be manually written or coming from the performer?

    description = fields.Text(
        help="Context of the impression: Why/how the assessment was performed"
    )
    # FHIR: description

    encounter_id = fields.Many2one("medical.encounter", required=True)
    # FHIR: encounter

    patient_id = fields.Many2one(related="encounter_id.patient_id")
    # FHIR: patient

    # FHIR: Effective date: needed?

    validation_date = fields.Datetime()
    # FHIR: date

    validation_user_id = fields.Many2one(
        "res.users", string="Validated by", readonly=True, copy=False
    )

    cancellation_date = fields.Datetime()

    cancellation_user_id =  fields.Many2one(
        "res.users", string="Cancelled by", readonly=True, copy=False
    )
    
    allergy_substance_ids = fields.Many2many(
        comodel_name="medical.allergy.substance",
    )
    condition_ids = fields.One2many(
        comodel_name="medical.condition",
        string="Conditions",
        related="patient_id.medical_condition_ids",
    )

    condition_count = fields.Integer(related="patient_id.medical_condition_count")

    family_history_ids = fields.Many2many(
        "medical.family.member.history", compute="_compute_family_history_ids"
    )

    family_history_count = fields.Integer(
        compute="_compute_family_history_count"
    )

    summary = fields.Text()
    # FHIR: summary

    finding_ids = fields.Many2many(comodel_name="medical.clinical.finding")
    # FHIR: finding

    note = fields.Text()
    # FHIR: Note

    @api.depends("patient_id", "patient_id.family_history_ids")
    def _compute_family_history_ids(self):
        self.family_history_ids = self.patient_id.family_history_ids

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.clinical.impression")
            or "/"
        )

    def _compute_clinical_impression_name(self):
        for rec in self:
            rec.name = _(
                "{} {}".format(rec.patient_id.name, rec.validation_date)
            )

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
                            "origin_clinical_impression_id": self.id
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
                            "origin_clinical_impression_id": self.id
                        }
                    )

    def _validate_clinical_impression_fields(self):
        return {
            "state": "completed",
            "validation_date": fields.Datetime.now(),
            "validation_user_id": self.env.user.id,
        }

    def validate_clinical_impression(self):
        self.ensure_one()
        self.write(self._validate_clinical_impression_fields())
        self._create_conditions_from_findings()
        self._create_allergies_from_findings()

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            rec.is_editable = rec._is_editable()

    def _is_editable(self):
        return self.state in ("in_progress",)

    def _cancel_clinical_impression_fields(self):
        return {
            "state": "cancelled",
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

    def action_create_familiar_history(self):
        self.ensure_one()
        familiar_history = self.env["medical.family.member.history"].create(
            {"patient_id": self.patient_id.id}
        )
        return familiar_history.get_formview_action()

    def action_view_family_history(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_impression."
            "medical_family_member_history_action"
        ).read()[0]
        action["domain"] = [
            ("patient_id", "=", self.patient_id.id),
        ]

        action["context"] = {"default_patient_id": self.patient_id.id}
        return action

    @api.depends("family_history_ids")
    def _compute_family_history_count(self):
        self.family_history_count = len(self.family_history_ids)

    
    # TODO: add emial thread to family and impressions
