# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalPatient(models.Model):
    # FHIR Entity: Patient (http://hl7.org/fhir/patient.html)
    _inherit = "medical.patient"

    coverage_ids = fields.One2many(
        string="Coverage",
        comodel_name="medical.coverage",
        inverse_name="patient_id",
    )
    coverage_count = fields.Integer(
        compute="_compute_coverage_count",
        string="# of Coverages",
        copy=False,
        default=0,
    )

    @api.depends("coverage_ids")
    def _compute_coverage_count(self):
        for record in self:
            record.coverage_count = len(record.coverage_ids)

    def action_view_coverage(self):
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_financial_coverage.medical_coverage_action"
        )
        result["context"] = {"default_patient_id": self.id}
        result["domain"] = "[('patient_id', '=', " + str(self.id) + ")]"
        if len(self.coverage_ids) == 1:
            res = self.env.ref("medical.coverage.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.coverage_ids.id
        return result
