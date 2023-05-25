# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields, models


class MedicalClinicalImpression(models.Model):
    _inherit = "medical.clinical.impression"

    auto_validated = fields.Boolean()

    def _cron_validate_clinical_impression(self, hours):
        to_validate = self.search(
            [
                ("fhir_state", "=", "in_progress"),
                (
                    "write_date",
                    "<",
                    fields.Datetime.now() + timedelta(hours=-hours),
                ),
            ]
        )
        for impression in to_validate:
            impression.with_user(
                impression.write_uid.id
            ).validate_clinical_impression(auto_validated=True)

    def _validate_clinical_impression_fields(
        self, auto_validated=False, **kwargs
    ):
        result = super()._validate_clinical_impression_fields(**kwargs)
        if auto_validated:
            result["auto_validated"] = True
        return result
