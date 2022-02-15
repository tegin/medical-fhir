# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalDiagnosticReportTemplate(models.Model):

    _inherit = "medical.diagnostic.report.template"

    graph_python_code = fields.Text()
    html_code = fields.Text(translate=True)

    def _generate_report_vals(self, encounter=None, **kwargs):
        res = super()._generate_report_vals(encounter, **kwargs)
        res["compute_graph"] = self.compute_graph
        res["compute_html"] = self.compute_html
        res["hide_observations"] = self.hide_observations
        return res
