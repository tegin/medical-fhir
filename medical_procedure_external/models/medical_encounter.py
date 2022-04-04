# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalEncounter(models.Model):

    _inherit = "medical.encounter"

    external_request_ids = fields.One2many(
        comodel_name="medical.procedure.external.request",
        inverse_name="encounter_id",
        domain=[("state", "!=", "cancelled")],
    )

    external_request_count = fields.Integer(
        compute="_compute_external_request_count"
    )

    @api.depends("external_request_ids")
    def _compute_external_request_count(self):
        for record in self:
            record.external_request_count = len(record.external_request_ids)

    def action_view_external_request(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_procedure_external.medical_procedure_external_request_act_window"
        ).read()[0]
        action["domain"] = [("encounter_id", "=", self.id)]
        action["context"] = {"search_default_filter_not_cancelled": True}
        return action
