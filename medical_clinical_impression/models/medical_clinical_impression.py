# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MedicalClinicalImpression(models.Model):

    _name = "medical.clinical.impression"
    _inherit = "medical.event"
    _description = "Medical Clinical Impression"

    @api.model
    def _get_states(self):
        return [
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ]

    name = fields.Char(compute="_compute_clinical_impression_name", copy=False)

    state = fields.Selection(default="in_progress", states={}, required=False)
    # TODO: add buttons to change state
    # Should cancelled be added?
    #   FHIR: status

    # FHIR statusreason: not needed I think
    @api.model
    def _get_impression_code(self):
        if self.create_uid.partner_id.specialty_ids:
            return self.create_uid.partner_id.specialty_ids[0].name
        else:
            return False

    code = fields.Many2one("medical.specialty", default=_get_impression_code)
    # FHIR code: type of clinical assessment performed.
    # Can be used as a tag. Which should be related model?
    # Related to the specialty?
    # It can be manually written or coming from the performer?

    description = fields.Text(
        help="Context of the impression: Why/how the assessment was performed"
    )
    # FHIR: description

    encounter_id = fields.Many2one("medical.encounter", readonly=True)
    # FHIR: encounter

    patient_id = fields.Many2one(related="encounter_id.patient_id")
    # FHIR: patient

    # FHIR: Effective date: needed?

    impression_date = fields.Datetime()
    # FHIR: date

    """
    performer_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("is_practitioner", "=", True)],
        ondelete="restrict",
        index=True,
        tracking=True,
    )
    """
    # The create_uid is used as the assessor
    # FHIR Field : assessor

    parent_impression_id = fields.Many2one(
        "medical.clinical.impression",
        index=True,
        help="Select an impression if this impression makes a reference "
        "to a previous one",
        domain='[("id", "!=", id)]',
    )
    # FHIR: previous

    condition_ids = fields.Many2many(
        comodel_name="medical.condition",
        string="Conditions",
        compute="_get_condition_ids",
    )
    condition_count = fields.Integer(
        compute="_compute_medical_condition_count",
        string="# of Conditions",
        copy=False,
    )

    warning_ids = fields.Many2many(
        comodel_name="medical.condition",
        # domain='[("patient_id", "=", patient_id), ("create_warning", "=", True)]',
        help="Conditions relevant for this clinical impression",
        compute="_get_warning_ids",
    )
    # FHIR: problem

    warnings_count = fields.Integer(
        compute="_compute_warnings_count",
        string="# of Warnings",
        copy=False,
        default=0,
    )

    investigation_ids = fields.Many2many(
        comodel_name="medical.clinical.investigation",
        help="Signs, symptoms...",
    )
    # FHIR: Investigation
    # Each investigation should have an investigation code (type)
    # and a item (an observation, a report, an imagins study...)

    # protocol_id = fields.One2many()
    # FHI: protocol (clinical protocol followed)
    # I think not needed for the moment

    summary = fields.Text()
    # FHIR: summary

    finding_ids = fields.Many2many(comodel_name="medical.clinical.finding")
    # FHIR: finding
    # In fact is a reference wit itemcodeable concept and a item reference.
    # IT should be related with the
    # classification ICD - CM (Clinical Modifications) (Diagnosis codes)

    # prognosis = fields.Text(help="Estimate of likely outcome")
    # FHIR: prognosis
    # In fact is a reference with prognosis reference and supportinginfo
    # I think not needed for the moment

    note = fields.Text()
    # FHIR: Note

    # TODO: Add careplan?

    # TODO: add a button to see diagnostic reports of this encounter?
    #  Or would it be better to add on the item reference of findings?

    # TODO: create wizard to create a clinical impressions

    # TODO: decide how to create medical conditions

    # TODO: add counts on button

    @api.depends("patient_id", "patient_id.medical_warning_ids")
    def _get_warning_ids(self):
        self.warning_ids = self.patient_id.medical_warning_ids

    @api.depends("patient_id", "patient_id.medical_condition_ids")
    def _get_condition_ids(self):
        self.condition_ids = self.patient_id.medical_condition_ids

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.clinical.impression")
            or "/"
        )

    @api.depends("patient_id", "condition_ids")
    def _compute_medical_condition_count(self):
        for record in self:
            record.condition_count = len(record.condition_ids)

    def _compute_clinical_impression_name(self):
        for rec in self:
            rec.name = _(
                "{} {}".format(rec.patient_id.name, rec.impression_date)
            )

    def action_view_medical_conditions(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_condition.medical_clinical_condition_action"
        )
        result = action.read()[0]
        result["context"] = {"default_patient_id": self.patient_id.id}
        result["domain"] = (
            "[('patient_id', '=', " + str(self.patient_id.id) + ")]"
        )
        return result

    def action_view_warnings(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_clinical_condition.medical_clinical_condition_action"
        )
        result = action.read()[0]
        result["context"] = {"default_patient_id": self.patient_id.id}
        result["domain"] = (
            "[('patient_id', '=', "
            + str(self.patient_id.id)
            + "), ('create_warning', '=', True)]"
        )
        return result

    @api.depends("warning_ids")
    def _compute_warnings_count(self):
        for record in self:
            record.warnings_count = len(record.warning_ids)

    def _validate_clinical_impression_fields(self):
        impression_date = (
            fields.Datetime.now()
            if not self.impression_date
            else self.impression_date
        )
        return {"state": "completed", "impression_date": impression_date}

    def validate_clinical_impression(self):
        self.ensure_one()
        self.write(self._validate_clinical_impression_fields())

    @api.depends("state")
    def _compute_is_editable(self):
        for rec in self:
            rec.is_editable = rec._is_editable()

    def _is_editable(self):
        return self.state in ("in_progress",)

    def _cancel_clinical_impression_fields(self):
        return {
            "state": "cancelled",
        }

    def cancel_clinical_impression(self):
        self.ensure_one()
        self.write(self._cancel_clinical_impression_fields())

    def action_create_condition(self):
        self.ensure_one()
        impression = self.env["medical.condition"].create(
            {
                "patient_id": self.patient_id.id,
                "clinical_finding_id": self.finding_ids[0].id
                if self.finding_ids
                else False,
            }
        )
        return impression.get_formview_action()
