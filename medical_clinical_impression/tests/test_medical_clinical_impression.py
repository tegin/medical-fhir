# Copyright 2022 Creu Blanca

from datetime import datetime

import freezegun

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase


class TestClinicalImpression(TransactionCase):
    def setUp(self):
        super(TestClinicalImpression, self).setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.finding_pregnant = self.env["medical.clinical.finding"].create(
            {
                "name": "Pregnant",
                "create_condition_from_clinical_impression": True,
            }
        )
        self.finding_eye_infection = self.env["medical.clinical.finding"].create(
            {
                "name": "Eye infection",
                "create_condition_from_clinical_impression": False,
            }
        )
        self.allergy_substance_pollen = self.env["medical.allergy.substance"].create(
            {
                "name": "Pollen",
                "description": "Pollen",
            }
        )
        self.allergy_substance_ibuprofen = self.env["medical.allergy.substance"].create(
            {
                "name": "Ibuprofen",
                "description": "Ibuprofen",
                "create_warning": True,
            }
        )
        self.specialty_cardiology = self.env["medical.specialty"].create(
            {"name": "Cardiology", "description": "Cardiology"}
        )
        self.specialty_gynecology = self.env["medical.specialty"].create(
            {"name": "Gynecology", "description": "Gynecology"}
        )

    def test_validate_impression_fields(self):
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        with freezegun.freeze_time("2022-01-01 00:00:00"):
            impression.validate_clinical_impression()
        self.assertEqual(impression.validation_date, datetime(2022, 1, 1, 0, 0, 0))
        self.assertEqual(impression.validation_user_id.id, self.env.user.id)
        self.assertEqual(impression.fhir_state, "completed")

    def test_create_condition_from_impression_finding(self):
        self.assertEqual(self.patient.medical_condition_count, 0)
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_gynecology.id,
                "finding_ids": [
                    (4, self.finding_pregnant.id),
                    (4, self.finding_eye_infection.id),
                ],
            }
        )
        # It should create a condition for pregnant finding only
        impression.validate_clinical_impression()
        self.assertEqual(self.patient.medical_condition_count, 1)
        self.assertEqual(
            self.patient.medical_condition_ids[0].clinical_finding_id.id,
            self.finding_pregnant.id,
        )
        # If a new impression is created with the same finding,
        # it should not create a condition
        impression_2 = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_gynecology.id,
                "finding_ids": [(4, self.finding_pregnant.id)],
            }
        )
        impression_2.validate_clinical_impression()
        self.assertEqual(self.patient.medical_condition_count, 1)
        self.assertEqual(
            self.patient.medical_condition_ids[0].clinical_finding_id.id,
            self.finding_pregnant.id,
        )

    def test_create_allergy_from_impression_allergy_substance(self):
        self.assertEqual(self.patient.medical_allergies_count, 0)
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_gynecology.id,
                "allergy_substance_ids": [(4, self.allergy_substance_ibuprofen.id)],
            }
        )
        impression.validate_clinical_impression()
        self.assertEqual(self.patient.medical_allergies_count, 1)
        self.assertEqual(
            self.patient.medical_allergy_ids[0].allergy_id.id,
            self.allergy_substance_ibuprofen.id,
        )
        # If a new impression is created with the same allergy substance,
        # it should not create an allergy
        impression_2 = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_gynecology.id,
                "allergy_substance_ids": [(4, self.allergy_substance_ibuprofen.id)],
            }
        )
        impression_2.validate_clinical_impression()
        self.assertEqual(self.patient.medical_allergies_count, 1)
        self.assertEqual(
            self.patient.medical_allergy_ids[0].allergy_id.id,
            self.allergy_substance_ibuprofen.id,
        )

    def test_cancel_impression(self):
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_gynecology.id,
                "allergy_substance_ids": [(4, self.allergy_substance_ibuprofen.id)],
            }
        )
        impression.validate_clinical_impression()
        self.assertEqual(self.patient.medical_allergies_count, 1)
        impression.cancel_clinical_impression()
        # The allergies and findings created in that impression should be cancelled too.
        self.patient.invalidate_recordset()
        self.assertEqual(self.patient.medical_allergies_count, 0)

    def _create_cancelled_impression(self):
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        impression.validate_clinical_impression()
        impression.cancel_clinical_impression()
        return impression

    def _grant_revalidate_group(self):
        group = self.env.ref(
            "medical_clinical_impression.group_clinical_impression_revalidate"
        )
        self.env.user.write({"groups_id": [(4, group.id)]})

    def test_write_guarded_field_cancelled_without_revalidate_group(self):
        impression = self._create_cancelled_impression()
        self.assertFalse(impression.can_revalidate)
        with self.assertRaises(AccessError):
            impression.write({"summary": "New summary"})

    def test_write_guarded_field_cancelled_with_revalidate_group(self):
        impression = self._create_cancelled_impression()
        self._grant_revalidate_group()
        impression.invalidate_recordset()
        self.assertTrue(impression.can_revalidate)
        impression.write({"summary": "New summary"})
        self.assertEqual(impression.summary, "New summary")

    def test_write_non_guarded_field_cancelled_without_revalidate_group(self):
        # finding_ids is not part of _revalidate_guarded_fields, so it can
        # still be written even on a cancelled impression.
        impression = self._create_cancelled_impression()
        impression.write({"finding_ids": [(4, self.finding_pregnant.id)]})
        self.assertIn(self.finding_pregnant, impression.finding_ids)

    def test_revalidate_cancelled_without_revalidate_group(self):
        impression = self._create_cancelled_impression()
        with self.assertRaises(AccessError):
            impression.validate_clinical_impression()

    def test_revalidate_cancelled_with_revalidate_group(self):
        impression = self._create_cancelled_impression()
        self._grant_revalidate_group()
        impression.invalidate_recordset()
        impression.validate_clinical_impression()
        self.assertEqual(impression.fhir_state, "completed")
