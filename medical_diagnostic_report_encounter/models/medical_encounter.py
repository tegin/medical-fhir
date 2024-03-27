from odoo import api, fields, models


class MedicalEncounter(models.Model):
    _inherit = "medical.encounter"

    report_ids = fields.One2many(
        comodel_name="medical.diagnostic.report",
        inverse_name="encounter_id",
        domain=[("fhir_state", "!=", "cancelled")],
    )

    report_count = fields.Integer(compute="_compute_report_count")

    @api.depends("report_ids")
    def _compute_report_count(self):
        for record in self:
            record.report_count = len(record.report_ids)

    def action_view_report(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_diagnostic_report.medical_diagnostic_report_act_window"
        )
        action["domain"] = [("encounter_id", "=", self.id)]
        action["context"] = {"search_default_filter_not_cancelled": True}
        return action
