# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    def active2completed(self):
        for record in self:
            if not record.activity_definition_id:
                continue

            for successor in record.activity_definition_id.successor_ids:
                if successor._check_successor(record):
                    successor.successor_id.execute_activity(
                        record._get_successor_vals(successor), parent=record
                    )
        return super().active2completed()

    def _get_successor_vals(self, successor):
        vals = {
            "patient_id": self.patient_id.id,
            "name": successor.successor_id.name,
        }
        for model in self._get_request_models():
            field_name = self.env[model]._get_parent_field_name()
        if getattr(self, field_name):
            vals[field_name] = getattr(self, field_name).id
        return vals
