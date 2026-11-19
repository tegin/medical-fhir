# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalReport(models.Model):
    _inherit = "medical.report"

    model = fields.Selection(
        selection_add=[("medical.procedure.external.request", "External Procedure")]
    )
    description = fields.Text()

    def _queries(self):
        return super()._queries() + [
            self._add_basic_query("medical.procedure.external.request")
        ]

    def _basic_query_medical_procedure_external_request_fields(self):
        return {
            "is_draft": "fhir_state = 'draft'",
            "is_cancelled": "fhir_state = 'cancelled'",
            "date": "issued_date",
            "description": "name",
            "user_id": "issued_user_id",
        }
