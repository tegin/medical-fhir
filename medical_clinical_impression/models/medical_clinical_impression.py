# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class MedicalClinicalImpression(models.Model):

    _name = "medical.clinical.impression"
    _inherit = ["medical.event", "mail.thread", "mail.activity.mixin"]
    _description = "Medical Clinical Impression"
    _conditions = "condition_ids"
    _order = "__last_update desc, id"
    _rec_name = "internal_identifier"

    _revalidate_guarded_fields = {
        "description",
        "note",
        "summary",
        "allergy_substance_ids",
    }

    def write(self, vals):
        if self._revalidate_guarded_fields.intersection(vals) and any(
            record.fhir_state == "cancelled" and not record.can_revalidate
            for record in self
        ):
            raise AccessError(
                _("You are not allowed to edit a cancelled clinical" " impression.")
            )
        return super().write(vals)

    @api.model
    def _get_states(self):
        return {
            "in_progress": ("In Progress", "draft"),
            "completed": ("Completed", "done"),
            "cancelled": ("Cancelled", "done"),
        }

    fhir_state = fields.Selection(default="in_progress", readonly=True)

    specialty_id = fields.Many2one("medical.specialty", required=True, readonly=True)
    # FHIR code: type of clinical assessment performed.
    # TODO: add domain, so a partner can only select between their specialities

    description = fields.Html(
        help="Context of the impression: Why/how the assessment was performed",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    # FHIR: description

    patient_id = fields.Many2one(
        "medical.patient",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    # FHIR: patient

    validation_date = fields.Datetime(readonly=True)
    # FHIR: date

    validation_user_id = fields.Many2one(
        "res.users", string="Validated by", readonly=True, copy=False
    )

    cancellation_date = fields.Datetime(readonly=True)

    cancellation_user_id = fields.Many2one(
        "res.users", string="Cancelled by", readonly=True, copy=False
    )
    finding_ids = fields.Many2many(
        comodel_name="medical.clinical.finding",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    # FHIR: finding
    allergy_substance_ids = fields.Many2many(
        comodel_name="medical.allergy.substance",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    condition_ids = fields.One2many(
        comodel_name="medical.condition",
        string="Conditions",
        related="patient_id.medical_condition_ids",
    )

    medical_condition_count = fields.Integer(
        related="patient_id.medical_condition_count"
    )

    summary = fields.Text(readonly=True, states={"draft": [("readonly", False)]})
    # FHIR: summary
    note = fields.Html(readonly=True, states={"draft": [("readonly", False)]})
    # FHIR: Note

    warning_info = fields.Json(compute="_compute_warning_info")

    can_revalidate = fields.Boolean(compute="_compute_can_revalidate")

    def _compute_can_revalidate(self):
        can_revalidate = self.env.user.has_group(
            "medical_clinical_impression.group_clinical_impression_revalidate"
        )
        for record in self:
            record.can_revalidate = can_revalidate

    def _get_warning_info(self):
        self.ensure_one()
        return {
            condition.id: {
                "name": condition.name,
                "create_date": fields.Date.to_string(condition.create_date),
                "create_warning": condition.create_warning,
            }
            for condition in self.condition_ids
        }

    @api.depends("condition_ids")
    def _compute_warning_info(self):
        for record in self:
            record.warning_info = record._get_warning_info()

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.clinical.impression") or "/"
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
        if self.fhir_state == "cancelled" and not self.can_revalidate:
            raise AccessError(
                _(
                    "You are not allowed to revalidate a cancelled clinical"
                    " impression."
                )
            )
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

    def action_create_clinical_impression_report(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_diagnostic_report.medical_patient_create_diagnostic_report_act_window"
        )
        action["context"] = {
            "default_patient_id": self.patient_id.id,
            "clinical_impression_id": self.id,
        }
        return action

    def impression_family_history(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Family Member History",
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "medical.family.member.history",
            "domain": [("patient_id", "=", self.patient_id.id)],
            "views": [
                (
                    self.env.ref(
                        "medical_clinical_impression.medical_family_member_history_view_tree"
                    ).id,
                    "tree",
                ),
                (
                    self.env.ref(
                        "medical_clinical_impression.medical_family_member_history_view_form"
                    ).id,
                    "form",
                ),
            ],
            "target": "current",
        }
