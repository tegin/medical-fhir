# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalProcedure(models.Model):
    # FHIR Entity: Procedure (https://www.hl7.org/fhir/procedure.html)
    _name = "medical.procedure"
    _description = "Medical Procedure"
    _inherit = "medical.event"

    internal_identifier = fields.Char(string="Procedure")
    procedure_request_id = fields.Many2one(
        comodel_name="medical.procedure.request",
        string="Procedure request",
        ondelete="restrict",
        index=True,
        readonly=True,
    )  # FHIR Field: BasedOn
    performed_initial_date = fields.Datetime(
        string="Initial date",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )  # FHIR Field: performed/performedPeriod
    performed_end_date = fields.Datetime(
        string="End date",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )  # FHIR Field: performed/performedPeriod
    location_id = fields.Many2one(
        comodel_name="res.partner",
        domain=[("is_location", "=", True)],
        ondelete="restrict",
        index=True,
        string="Location",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )  # FHIR Field: location

    @api.constrains("procedure_request_id")
    def _check_procedure(self):
        if len(self.procedure_request_id.procedure_ids) > 1:
            raise ValidationError(
                _(
                    "You cannot create more than one Procedure "
                    "for each Procedure Request."
                )
            )
        if not self.env.context.get("no_check_patient", False):
            if self.patient_id != self.procedure_request_id.patient_id:
                raise ValidationError(_("Patient inconsistency"))

    def _get_internal_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.procedure") or "/"

    def preparation2in_progress_values(self):
        res = super().preparation2in_progress_values()
        res["performed_initial_date"] = fields.Datetime.now()
        return res

    def in_progress2completed_values(self):
        res = super().in_progress2completed_values()
        res["performed_end_date"] = fields.Datetime.now()
        return res
