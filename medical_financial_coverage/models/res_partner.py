# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    # FHIR Entity: Payor
    # (https://www.hl7.org/fhir/coverage-definitions.html#Coverage.payor)
    _inherit = "res.partner"

    is_payor = fields.Boolean(default=False)
    payor_identifier = fields.Char(readonly=True)  # FHIR Field: identifier
    coverage_template_ids = fields.One2many(
        string="Coverage Template",
        comodel_name="medical.coverage.template",
        inverse_name="payor_id",
    )
    coverage_template_count = fields.Integer(
        compute="_compute_coverage_template_count",
        string="# of Templates",
        copy=False,
        default=0,
    )

    @api.model
    def _get_medical_identifiers(self):
        res = super(ResPartner, self)._get_medical_identifiers()
        res.append(
            (
                "is_medical",
                "is_payor",
                "payor_identifier",
                self._get_payor_identifier,
            )
        )
        return res

    def _compute_coverage_template_count(self):
        for rec in self:
            rec.coverage_template_count = len(rec.coverage_template_ids)

    @api.model
    def _get_payor_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.payor") or "/"

    def action_view_coverage_template(self):
        action = self.env.ref(
            "medical_financial_coverage.medical_coverage_template_action"
        )
        result = action.read()[0]
        result["context"] = {"default_payor_id": self.id}
        result["domain"] = "[('payor_id', '=', " + str(self.id) + ")]"
        if len(self.coverage_template_ids) == 1:
            res = self.env.ref("medical.coverage.template.view.form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = self.coverage_template_ids.id
        return result
