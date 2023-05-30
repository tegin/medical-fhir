# Copyright 2022 Creu Blanca

import freezegun

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMedicalPatient(TransactionCase):
    def setUp(self):
        super(TestMedicalPatient, self).setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.specialty_cardiology = self.env["medical.specialty"].create(
            {"name": "Cardiology", "description": "Cardiology"}
        )
        self.specialty_gynecology = self.env["medical.specialty"].create(
            {"name": "Gynecology", "description": "Gynecology"}
        )

    def test_create_impression_from_patient_impression_view(self):
        self.encounter = self.env["medical.encounter"].create(
            {
                "patient_id": self.patient.id,
                "create_date": fields.Datetime.now(),
            }
        )
        wizard = self.env["create.impression.from.patient"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        wizard = wizard.with_context(impression_view=True)
        action = wizard.generate()

        self.assertEqual(action["type"], "ir.actions.act_multi")
        self.assertEqual(len(action["actions"]), 2)
        self.assertEqual(
            action["actions"][0]["type"], "ir.actions.act_window_close"
        )
        self.assertEqual(
            action["actions"][1]["type"], "ir.actions.act_select_record"
        )
        self.assertFalse(wizard.show_encounter_warning)

    def test_create_impression_from_patient_without_encounter(self):
        with self.assertRaises(ValidationError):
            self.env["create.impression.from.patient"].create(
                {
                    "patient_id": self.patient.id,
                    "specialty_id": self.specialty_cardiology.id,
                }
            ).generate()

    def test_create_impression_from_patient_with_old_encounter(self):
        with freezegun.freeze_time("2022-01-01"):
            self.encounter = self.env["medical.encounter"].create(
                {
                    "patient_id": self.patient.id,
                    "create_date": fields.Datetime.now(),
                }
            )
        with freezegun.freeze_time("2022-02-01"):
            wizard = self.env["create.impression.from.patient"].create(
                {
                    "patient_id": self.patient.id,
                    "encounter_id": self.encounter.id,
                    "specialty_id": self.specialty_cardiology.id,
                }
            )
            wizard._onchange_encounter_date()
            self.assertTrue(wizard.show_encounter_warning)

    def test_create_impression_from_patient_with_recent_encounter(self):
        with freezegun.freeze_time("2022-02-01"):
            self.encounter = self.env["medical.encounter"].create(
                {
                    "patient_id": self.patient.id,
                    "create_date": fields.Datetime.now(),
                }
            )
            wizard = self.env["create.impression.from.patient"].create(
                {
                    "patient_id": self.patient.id,
                    "encounter_id": self.encounter.id,
                    "specialty_id": self.specialty_cardiology.id,
                }
            )
            wizard._onchange_encounter_date()
            self.assertFalse(wizard.show_encounter_warning)

    def test_create_impression_from_patient_get_last_encounter(self):
        with freezegun.freeze_time("2022-01-01"):
            self.encounter_old = self.env["medical.encounter"].create(
                {
                    "patient_id": self.patient.id,
                    "create_date": fields.Datetime.now(),
                }
            )
        with freezegun.freeze_time("2022-02-01"):
            self.encounter_recent = self.env["medical.encounter"].create(
                {
                    "patient_id": self.patient.id,
                    "create_date": fields.Datetime.now(),
                }
            )
        self.patient.refresh()
        with freezegun.freeze_time("2022-02-03"):
            wizard = self.env["create.impression.from.patient"].create(
                {
                    "patient_id": self.patient.id,
                    "specialty_id": self.specialty_cardiology.id,
                }
            )
            self.assertEqual(wizard.encounter_id.id, self.encounter_recent.id)
            self.assertFalse(wizard.show_encounter_warning)
        action = wizard.generate()
        self.assertEqual(
            "medical.clinical.impression", action.get("res_model")
        )
        self.assertEqual(
            action["context"]["default_encounter_id"], self.encounter_recent.id
        )
        self.assertEqual(
            action["context"]["default_specialty_id"],
            self.specialty_cardiology.id,
        )

    def test_view_clinical_impressions_from_patient(self):
        self.encounter = self.env["medical.encounter"].create(
            {
                "patient_id": self.patient.id,
                "create_date": fields.Datetime.now(),
            }
        )
        self.patient.refresh()
        action = self.patient.action_view_clinical_impressions()
        self.assertEqual(action["res_model"], "medical.clinical.impression")
        self.assertEqual(
            action["context"]["default_encounter_id"], self.encounter.id
        )
        self.assertEqual(
            action["context"]["search_default_filter_not_cancelled"], True
        )

    def test_compute_impression_specialties_from_patient(self):
        self.encounter = self.env["medical.encounter"].create(
            {
                "patient_id": self.patient.id,
            }
        )
        self.patient.refresh()
        self.assertEqual(len(self.patient.medical_impression_ids.ids), 0)
        self.assertEqual(len(self.patient.impression_specialty_ids.ids), 0)
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_gynecology.id,
            }
        )
        self.assertEqual(len(self.patient.medical_impression_ids.ids), 3)
        self.assertEqual(len(self.patient.impression_specialty_ids.ids), 2)

    def test_create_family_history_from_patient(self):
        action = self.patient.create_family_member_history()
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )
        # It opens a wizard, if not saved should not create a record,
        # for this reason count should be 0.
        self.assertEqual(self.patient.family_history_count, 0)
        self.env["medical.family.member.history"].create(
            {
                "patient_id": self.patient.id,
                "relationship": "Father",
                "note": "Prostate cancer",
            }
        )
        self.assertEqual(self.patient.family_history_count, 1)
        self.assertEqual(
            self.patient.family_history_ids[0].name,
            "Family History of Patient",
        )

    def test_view_family_history_from_patient(self):
        action = self.patient.action_view_family_history()
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )

    def test_action_view_family_history_tree(self):
        action = self.patient.action_view_family_history_tree()
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )
        self.assertEqual(
            action["views"],
            [
                (
                    self.env.ref(
                        "medical_clinical_impression.medical_family_member_history_view_tree"
                    ).id,
                    "list",
                )
            ],
        )

    def test_compute_impression_info_from_patient(self):
        self.encounter = self.env["medical.encounter"].create(
            {
                "patient_id": self.patient.id,
            }
        )
        # Impression 1 in_progress
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        # Impression 2 in_progress
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        # Impression 3 completed
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_cardiology.id,
                "fhir_state": "completed",
            }
        )
        # Impression 4 gynecology (should not be considered in the impression_count)
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
                "specialty_id": self.specialty_gynecology.id,
            }
        )
        self.specialty_cardiology.with_context(
            {"patient_id": self.patient.id}
        )._compute_impression_info()
        self.assertEqual(self.specialty_cardiology.patient_impression_count, 3)
        self.assertEqual(
            self.specialty_cardiology.impressions_in_progress_count, 2
        )

    def test_get_specialty_impressions_from_patient(self):
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
            {"patient_id": self.patient.id}
        ).get_specialty_impression()
        self.assertEqual(
            action["context"]["default_encounter_id"], self.encounter_2.id
        )

    def test_get_patient_data(self):
        # Create a new patient with attributes for testing
        new_patient = self.env["medical.patient"].create(
            {
                "name": "New Patient",
                "gender": "female",
                "birth_date": "1998-10-12",
            }
        )
        encounter = self.env["medical.encounter"].create(
            {"patient_id": new_patient.id}
        )
        finding_pregnant = self.env["medical.clinical.finding"].create(
            {
                "name": "Pregnant",
                "create_condition_from_clinical_impression": True,
            }
        )
        finding_eye_infection = self.env["medical.clinical.finding"].create(
            {
                "name": "Eye infection",
                "create_condition_from_clinical_impression": False,
            }
        )

        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": new_patient.id,
                "encounter_id": encounter.id,
                "specialty_id": self.specialty_gynecology.id,
                "finding_ids": [
                    (4, finding_pregnant.id),
                    (4, finding_eye_infection.id),
                ],
            }
        )

        impression.validate_clinical_impression()

        # Call the function being tested
        patient_data = new_patient.get_patient_data()

        # Assert the expected output
        self.assertEqual(patient_data["name"], "New Patient")
        self.assertEqual(patient_data["condition_count"], 1)
        self.assertCountEqual(patient_data["condition_names"], ["Pregnant"])
        self.assertEqual(patient_data["gender"], "Female")
        self.assertEqual(patient_data["patient_age"], 24)
