# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalDiagnosticReportExpand(models.TransientModel):

    _inherit = "medical.diagnostic.report.expand"

    def _merge_new_vals(self, vals):
        new_vals = super()._merge_new_vals(self, vals)
        if (
            vals["compute_graph"]
            and not self.diagnostic_report_id.compute_graph
        ):
            new_vals.update({"compute_graph": vals["compute_graph"]})
        if vals["compute_html"] and not self.diagnostic_report_id.compute_html:
            new_vals.update({"compute_html": vals["compute_html"]})
        if (
            vals["hide_observations"]
            and not self.diagnostic_report_id.compute_graph
        ):
            new_vals.update({"hide_observations": vals["hide_observations"]})
        return new_vals
