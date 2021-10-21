# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MedicalClinicalImpression(models.Model):

    _name = "medical.clinical.impression"
    _inherit = "medical.abstract"
    _description = "Medical Clinical Impression"

    name = fields.Char(compute="_compute_clinical_impression_name")

    state = fields.Selection(
        [("in_progress", "In Progress"), ("completed", "Completed")],
        default="in_progress",
    )
    # TODO: add buttons to change state
    # Should cancelled be added?
    #   FHIR: status

    # FHIR statusreason: not needed I think

    code = fields.Many2one("medical.specialty")
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

    patient_id = fields.Many2one(
        "medical.patient", related="encounter_id.patient_id"
    )
    # FHIR: patient

    # FHIR: Effective date: needed?

    impression_date = fields.Datetime(required=True)
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
        domain='[("patient_id", "=", patient_id)]',
        help="Conditions relevant for this clinical impression",
    )
    # FHIR: problem

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

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.clinical.impression")
            or "/"
        )

    def _compute_clinical_impression_name(self):
        for rec in self:
            rec.name = _(
                "%s Clinical Impression %s"
                % (rec.patient_id.name, rec.impression_date)
            )
