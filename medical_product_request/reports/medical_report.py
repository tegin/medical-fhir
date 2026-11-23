# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalReport(models.Model):
    _inherit = "medical.report"

    model = fields.Selection(
        selection_add=[
            ("medical.product.request.order", "Medical Product Request Order")
        ]
    )
    description = fields.Text()

    def _queries(self):
        return super()._queries() + [
            self._add_basic_query("medical.product.request.order")
        ]

    def _basic_query_medical_product_request_order_fields(self):
        return {
            "is_draft": "state = 'draft'",
            "is_cancelled": "state = 'cancelled'",
            "date": "validation_date",
            "description": "name",
            "user_id": "requester_id",
            "has_download_report": "true",
        }
