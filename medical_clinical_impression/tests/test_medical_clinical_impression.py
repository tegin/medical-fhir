# Copyright 2022 Creu Blanca

from datetime import datetime

import freezegun
from odoo.tests.common import TransactionCase


class TestClinicalImpression(TransactionCase):
    def setUp(self):
        super(TestClinicalImpression, self).setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id}
        )
        self.finding_pregnant = self.env["medical.clinical.finding"].create(
            {
                "name": "Pregnant",
                "create_condition_from_clinical_impression": True,
            }
        )
        self.finding_eye_infection = self.env[
            "medical.clinical.finding"
        ].create(
            {
                "name": "Eye infection",
                "create_condition_from_clinical_impression": False,
            }
        )
        self.allergy_substance_pollen = self.env[
            "medical.allergy.substance"
        ].create(
            {
                "name": "Pollen",
                "description": "Pollen",
            }
        )
        self.allergy_substance_ibuprofen = self.env[
            "medical.allergy.substance"
        ].create(
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
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        with freezegun.freeze_time("2022-01-01 00:00:00"):
            impression.validate_clinical_impression()
        self.assertEqual(
            impression.validation_date, datetime(2022, 1, 1, 0, 0, 0)
        )
        self.assertEqual(impression.validation_user_id.id, self.env.user.id)
        self.assertEqual(impression.state, "completed")

    def test_create_condition_from_impression_finding(self):
        self.assertEqual(self.patient.medical_condition_count, 0)
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
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
                "encounter_id": self.encounter.id,
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
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_gynecology.id,
                "allergy_substance_ids": [
                    (4, self.allergy_substance_ibuprofen.id)
                ],
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
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_gynecology.id,
                "allergy_substance_ids": [
                    (4, self.allergy_substance_ibuprofen.id)
                ],
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
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_gynecology.id,
                "allergy_substance_ids": [
                    (4, self.allergy_substance_ibuprofen.id)
                ],
            }
        )
        impression.validate_clinical_impression()
        self.assertEqual(self.patient.medical_allergies_count, 1)
        impression.cancel_clinical_impression()
        # The allergies and findings created in that impression should be cancelled too.
        self.patient.refresh()
        self.assertEqual(self.patient.medical_allergies_count, 0)

    def test_compute_current_encounter(self):
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_gynecology.id,
            }
        )
        self.encounter_2 = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id}
        )
        impression.with_context(
            {"encounter_id": self.encounter.id}
        )._compute_current_encounter()
        self.assertTrue(impression.current_encounter)
        impression.with_context(
            {"encounter_id": self.encounter_2.id}
        )._compute_current_encounter()
        self.assertFalse(impression.current_encounter)

    def test_compute_is_editable(self):
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_gynecology.id,
            }
        )
        self.assertTrue(impression.is_editable)
        impression.validate_clinical_impression()
        self.assertFalse(impression.is_editable)
        impression.cancel_clinical_impression()
        self.assertFalse(impression.is_editable)
