# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalEncounter(models.Model):

    _inherit = "medical.encounter"

    report_ids = fields.One2many(
        comodel_name="medical.diagnostic.report",
        inverse_name="encounter_id",
        domain=[("state", "!=", "cancelled")],
    )

    report_count = fields.Integer(compute="_compute_report_count")

    @api.depends("report_ids")
    def _compute_report_count(self):
        for record in self:
            record.report_count = len(record.report_ids)

    def action_view_report(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_diagnostic_report.medical_diagnostic_report_act_window"
        ).read()[0]
        action["domain"] = [("encounter_id", "=", self.id)]
        action["context"] = {"search_default_filter_not_cancelled": True}
        return action
