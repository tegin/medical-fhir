from odoo import fields, models


class MedicalDiagnosticReport(models.Model):

    _inherit = "medical.diagnostic.report"

    encounter_id = fields.Many2one("medical.encounter", readonly=True)

    def _generate_serializer(self):
        result = super(MedicalDiagnosticReport, self)._generate_serializer()
        result.update(
            {
                "encounter_id": self.encounter_id.id,
            }
        )
        return result
