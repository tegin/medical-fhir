from odoo import models


class PrintMedicalDiagnosticReport(models.AbstractModel):
    _name = "report.medical_diagnostic_report.report_template"
    _inherit = "report.report_external_pdf.abstract"
    _description = "PrintMedicalDiagnosticReport"

    def _render_report(self, docids, data):
        """This function allows to choose the template
        of the report depending on the report_action_id.
        But it has some limitations. It only allows to choose
        the template when printing only one report.
        If several reports are printed at the same time,
        the default template will be used"""

        diagnostic_reports = self.env["medical.diagnostic.report"].browse(
            docids
        )
        if (
            len(diagnostic_reports) == 1
            and diagnostic_reports.report_action_id
        ):
            action = self.env["ir.actions.report"]._get_report_from_name(
                diagnostic_reports.report_action_id.report_name
            )
        else:
            action = self.env.ref(
                "medical_diagnostic_report.medical_diagnostic_report_standard"
            )
        action_report = action.render(docids)
        return action_report[0]
