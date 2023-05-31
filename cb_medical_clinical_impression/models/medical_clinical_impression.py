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

    def action_create_clinical_impression_report(self):
        self.mapped("patient_id").ensure_one()
        self.mapped("specialty_id").ensure_one()
        report = self.env["medical.diagnostic.report"].create(
            self._create_diagnostic_report_vals()
        )
        return report.get_formview_action()

    def _create_diagnostic_report_vals(self):
        encounter = self[0].encounter_id
        return {
            "encounter_id": encounter.id,
            "patient_name": encounter.patient_id.name,
            "vat": encounter.patient_id.vat,
            "patient_age": self.env[
                "medical.diagnostic.report.template"
            ]._compute_age(encounter.patient_id),
            "composition": self._get_report_composition(),
            "name": self[0].specialty_id.name,
            "lang": self.env.context.get("lang") or self.env.user.lang,
            "item_blocked": False,
            "with_conclusion": False,
            "with_observation": False,
            "with_composition": True,
        }

    def _get_report_composition(self):
        return self.env["ir.qweb"]._render(
            "cb_medical_clinical_impression.impression_to_diagnostic_report",
            {"impressions": self},
        )
