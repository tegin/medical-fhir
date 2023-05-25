# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo.tests.common import SavepointCase


class TestAutomaticValidation(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["medical.patient"].create({"name": "Jane Doe"})
        cls.encounter = cls.env["medical.encounter"].create(
            {"patient_id": cls.patient.id}
        )
        cls.specialty = cls.env["medical.specialty"].create(
            {"name": "Demo specialty", "description": "Demo"}
        )

    def test_cron_validate_clinical_impression(self):
        self.assertFalse(self.patient.medical_impression_ids)
        self.env["create.impression.from.patient"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty.id,
            }
        ).generate()
        self.assertTrue(self.patient.medical_impression_ids)
        impression = self.patient.medical_impression_ids
        self.assertEqual(impression.fhir_state, "in_progress")

        self.env[
            "medical.clinical.impression"
        ]._cron_validate_clinical_impression(5)

        self.assertEqual(impression.fhir_state, "in_progress")
        with freeze_time(datetime.now() + timedelta(hours=2)):
            self.env[
                "medical.clinical.impression"
            ]._cron_validate_clinical_impression(5)
        self.assertEqual(impression.fhir_state, "in_progress")
        with freeze_time(datetime.now() + timedelta(hours=6)):
            self.env[
                "medical.clinical.impression"
            ]._cron_validate_clinical_impression(5)
        self.assertEqual(impression.fhir_state, "completed")
        self.assertTrue(impression.auto_validated)
