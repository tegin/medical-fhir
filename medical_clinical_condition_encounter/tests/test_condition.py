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
        self.allergy_substance_warning = self.env["medical.allergy.substance"].create(
            {"name": "Allergy substance warning", "create_warning": True}
        )

    def test_create_condition_from_encounter(self):
        action = self.encounter.create_medical_clinical_condition()
        self.assertEqual(action["context"]["default_patient_id"], self.patient.id)

    def test_view_conditions_from_encounter(self):
        res = self.encounter.action_view_medical_conditions()
        self.assertEqual(res["context"]["default_patient_id"], self.patient.id)

    def test_create_allergy_from_encounter(self):
        action = self.encounter.create_allergy()
        self.assertEqual(action["context"]["default_patient_id"], self.patient.id)
        self.assertTrue(action["context"]["default_is_allergy"])

    def test_view_allergies_from_encounter(self):
        res = self.encounter.action_view_medical_allergies()
        self.assertEqual(res["context"]["default_patient_id"], self.patient.id)
        self.assertTrue(res["context"]["default_is_allergy"])

    def test_view_warnings_from_encounter(self):
        res = self.encounter.action_view_medical_warnings()
        self.assertEqual(res["context"]["default_patient_id"], self.patient.id)
