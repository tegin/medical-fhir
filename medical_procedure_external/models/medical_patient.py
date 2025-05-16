# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalPatient(models.Model):

    _inherit = "medical.patient"

    external_request_ids = fields.One2many(
        comodel_name="medical.procedure.external.request",
        inverse_name="patient_id",
        domain="[('fhir_state', '!=', 'cancelled')]",
    )

    external_request_count = fields.Integer(compute="_compute_external_request_count")

    external_request_ids_filtered = fields.One2many(
        comodel_name="medical.procedure.external.request",
        inverse_name="patient_id",
        compute="_compute_filtered_requests",
        string="Filtered External Requests",
    )

    @api.depends("external_request_ids", "external_request_ids.fhir_state")
    def _compute_filtered_requests(self):
        for rec in self:
            rec.external_request_ids_filtered = rec.external_request_ids.filtered(
                lambda r: r.fhir_state != "cancelled"
            )

    @api.depends("external_request_ids")
    def _compute_external_request_count(self):
        for record in self:
            record.external_request_count = len(
                record.external_request_ids.filtered(lambda r: r.state != "cancelled")
            )

    def action_view_external_request(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_procedure_external.medical_procedure_external_request_act_window"
        ).read()[0]
        action["domain"] = [("patient_id", "=", self.id)]
        action["context"] = {"search_default_filter_not_cancelled": True}
        return action
