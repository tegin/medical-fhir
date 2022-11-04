# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestCondition(TransactionCase):
    def setUp(self):
        super(TestCondition, self).setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id}
        )
        self.finding_no_warning = self.env["medical.clinical.finding"].create(
            {"name": "Finding no warning"}
        )
        self.finding_warning = self.env["medical.clinical.finding"].create(
            {"name": "Finding warning", "create_warning": True}
        )
        self.allergy_substance_no_warning = self.env[
            "medical.allergy.substance"
        ].create({"name": "Allergy substance no warning"})
        self.allergy_substance_warning = self.env[
            "medical.allergy.substance"
        ].create({"name": "Allergy substance warning", "create_warning": True})

    def test_create_condition_from_patient(self):
        action = self.patient.create_medical_clinical_condition()
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )

    def test_create_condition_from_encounter(self):
        action = self.encounter.create_medical_clinical_condition()
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )

    def test_view_conditions_from_patient(self):
        res = self.patient.action_view_medical_conditions()
        self.assertEqual(res["context"]["default_patient_id"], self.patient.id)

    def test_view_conditions_from_encounter(self):
        res = self.encounter.action_view_medical_conditions()
        self.assertEqual(res["context"]["default_patient_id"], self.patient.id)

    def test_create_condition_without_warning(self):
        condition_no_warning = self.env["medical.condition"].create(
            {
                "patient_id": self.patient.id,
                "clinical_finding_id": self.finding_no_warning.id,
            }
        )
        self.assertEqual(condition_no_warning.name, "Finding no warning")
        self.assertFalse(condition_no_warning.create_warning)
        self.assertEqual(self.patient.medical_condition_count, 1)
        self.assertEqual(self.patient.medical_warning_count, 0)

    def test_create_condition_with_warning(self):
        condition_warning = self.env["medical.condition"].create(
            {
                "patient_id": self.patient.id,
                "clinical_finding_id": self.finding_warning.id,
            }
        )
        self.assertEqual(condition_warning.name, "Finding warning")
        self.assertTrue(condition_warning.create_warning)
        self.assertEqual(self.patient.medical_condition_count, 1)
        self.assertEqual(self.patient.medical_warning_count, 1)

    def test_create_allergy_from_patient(self):
        action = self.patient.create_allergy()
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )
        self.assertTrue(action["context"]["default_is_allergy"])

    def test_create_allergy_from_encounter(self):
        action = self.encounter.create_allergy()
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )
        self.assertTrue(action["context"]["default_is_allergy"])

    def test_create_allergy_without_warning(self):
        allergy_no_warning = self.env["medical.condition"].create(
            {
                "patient_id": self.patient.id,
                "is_allergy": True,
                "allergy_id": self.allergy_substance_no_warning.id,
            }
        )
        self.assertEqual(
            allergy_no_warning.name, "Allergy to Allergy substance no warning"
        )
        self.assertFalse(allergy_no_warning.create_warning)
        self.assertEqual(self.patient.medical_allergies_count, 1)
        self.assertEqual(self.patient.medical_warning_count, 0)

    def test_create_allergy_with_warning(self):
        allergy_warning = self.env["medical.condition"].create(
            {
                "patient_id": self.patient.id,
                "is_allergy": True,
                "allergy_id": self.allergy_substance_warning.id,
            }
        )
        self.assertEqual(
            allergy_warning.name, "Allergy to Allergy substance warning"
        )
        self.assertTrue(allergy_warning.create_warning)
        self.assertEqual(self.patient.medical_allergies_count, 1)
        self.assertEqual(self.patient.medical_warning_count, 1)

    def test_view_allergies_from_patient(self):
        res = self.patient.action_view_medical_allergies()
        self.assertEqual(res["context"]["default_patient_id"], self.patient.id)
        self.assertTrue(res["context"]["default_is_allergy"])

    def test_view_allergies_from_encounter(self):
        res = self.encounter.action_view_medical_allergies()
        self.assertEqual(res["context"]["default_patient_id"], self.patient.id)
        self.assertTrue(res["context"]["default_is_allergy"])

    def test_view_warnings_from_patient(self):
        res = self.patient.action_view_medical_warnings()
        self.assertEqual(res["context"]["default_patient_id"], self.patient.id)

    def test_view_warnings_from_encounter(self):
        res = self.encounter.action_view_medical_warnings()
        self.assertEqual(res["context"]["default_patient_id"], self.patient.id)

    def test_create_again_an_archived_condition(self):
        self.assertEqual(self.patient.medical_condition_count, 0)
        condition = self.env["medical.condition"].create(
            {
                "patient_id": self.patient.id,
                "clinical_finding_id": self.finding_warning.id,
            }
        )
        self.assertEqual(self.patient.medical_condition_count, 1)
        condition.toggle_active()
        self.patient.refresh()
        self.assertEqual(self.patient.medical_condition_count, 0)
        condition_2 = self.env["medical.condition"].create(
            {
                "patient_id": self.patient.id,
                "clinical_finding_id": self.finding_warning.id,
            }
        )
        self.patient.refresh()
        self.assertEqual(self.patient.medical_condition_count, 1)
        self.assertEqual(condition.id, condition_2.id)
