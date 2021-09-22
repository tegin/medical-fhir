# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalDiagnosticReportTemplate(models.Model):

    _inherit = "medical.diagnostic.report.template"

    graph_python_code = fields.Text()

    # TODO: Put it with kwargs
    def _generate_report_vals(self, encounter):
        res = super()._generate_report_vals(encounter)
        res["compute_graph"] = self.compute_graph
        res["hide_observations"] = self.hide_observations
        return res
