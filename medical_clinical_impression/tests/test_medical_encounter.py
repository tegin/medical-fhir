# Copyright 2022 Creu Blanca

import freezegun
from odoo import fields
from odoo.tests.common import TransactionCase


class TestMedicalEncounter(TransactionCase):
    def setUp(self):
        super(TestMedicalEncounter, self).setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.specialty_cardiology = self.env["medical.specialty"].create(
            {"name": "Cardiology", "description": "Cardiology"}
        )
        self.specialty_gynecology = self.env["medical.specialty"].create(
            {"name": "Gynecology", "description": "Gynecology"}
        )

    def test_create_impression_from_encounter_with_old_encounter(self):
        with freezegun.freeze_time("2022-01-01"):
            self.encounter = self.env["medical.encounter"].create(
                {
                    "patient_id": self.patient.id,
                    "create_date": fields.Datetime.now(),
                }
            )
        with freezegun.freeze_time("2022-02-01"):
            wizard = self.env["create.impression.from.encounter"].create(
                {
                    "patient_id": self.patient.id,
                    "encounter_id": self.encounter.id,
                    "specialty_id": self.specialty_cardiology.id,
                }
            )
            wizard._onchange_encounter_date()
            self.assertTrue(wizard.show_encounter_warning)
        action = wizard.generate()
        self.assertEqual(
            "medical.clinical.impression", action.get("res_model")
        )
        self.assertEqual(
            action["context"]["default_encounter_id"], self.encounter.id
        )
        self.assertEqual(
            action["context"]["default_specialty_id"],
            self.specialty_cardiology.id,
        )

    def test_view_clinical_impressions_from_encounter(self):
        self.encounter = self.env["medical.encounter"].create(
            {
                "patient_id": self.patient.id,
                "create_date": fields.Datetime.now(),
            }
        )
        action = self.encounter.action_view_clinical_impressions()
        self.assertEqual(action["res_model"], "medical.clinical.impression")
        self.assertEqual(
            action["context"]["default_encounter_id"], self.encounter.id
        )
        self.assertEqual(
            action["context"]["search_default_filter_not_cancelled"], True
        )

    def test_create_family_history_from_encounter(self):
        self.encounter = self.env["medical.encounter"].create(
            {
                "patient_id": self.patient.id,
                "create_date": fields.Datetime.now(),
            }
        )
        action = self.encounter.create_family_member_history()
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )
        # It opens a wizard, if not saved should not create a record,
        # for this reason count should be 0.
        self.assertEqual(self.encounter.family_history_count, 0)
        self.env["medical.family.member.history"].create(
            {
                "patient_id": self.patient.id,
                "relationship": "Father",
                "note": "Prostate cancer",
            }
        )
        self.assertEqual(self.encounter.family_history_count, 1)

    def test_view_family_history_from_encounter(self):
        self.encounter = self.env["medical.encounter"].create(
            {
                "patient_id": self.patient.id,
                "create_date": fields.Datetime.now(),
            }
        )
        action = self.encounter.action_view_family_history()
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )

    def test_compute_impression_info_from_encounter(self):
        self.encounter_1 = self.env["medical.encounter"].create(
            {
                "patient_id": self.patient.id,
            }
        )
        self.encounter_2 = self.env["medical.encounter"].create(
            {
                "patient_id": self.patient.id,
            }
        )
        # Impression 1 in_progress
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter_1.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        # Impression 2 in_progress
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter_2.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        # Impression 3 completed
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter_1.id,
                "specialty_id": self.specialty_cardiology.id,
                "state": "completed",
            }
        )
        # Impression 4 gynecology (should not be considered in the impression_count)
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter_2.id,
                "specialty_id": self.specialty_gynecology.id,
            }
        )
        self.specialty_cardiology.with_context(
            {"encounter_id": self.encounter_1.id}
        )._compute_impression_info()
        self.assertEqual(self.specialty_cardiology.patient_impression_count, 3)
        self.assertEqual(
            self.specialty_cardiology.encounter_impression_count, 2
        )
        self.assertEqual(
            self.specialty_cardiology.impressions_in_progress_count, 2
        )

    def test_get_specialty_impressions_from_encounter(self):
        with freezegun.freeze_time("2022-01-01"):
            self.encounter_1 = self.env["medical.encounter"].create(
                {
                    "patient_id": self.patient.id,
                    "create_date": fields.Datetime.now(),
                }
            )
        with freezegun.freeze_time("2022-02-01"):
            self.encounter_2 = self.env["medical.encounter"].create(
                {
                    "patient_id": self.patient.id,
                    "create_date": fields.Datetime.now(),
                }
            )
        self.patient.refresh()
        action = self.specialty_cardiology.with_context(
            {"encounter_id": self.encounter_1.id}
        ).get_specialty_impression()
        self.assertEqual(
            action["context"]["default_encounter_id"], self.encounter_1.id
        )
