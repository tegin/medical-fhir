# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase


class TestMedicalObservation(TransactionCase):
    def setUp(self):
        super(TestMedicalObservation, self).setUp()
        self.patient_1 = self.env["medical.patient"].create(
            {"name": "Patient 1", "vat": "47238567H"}
        )

    def test_compute_interpretation_float(self):
        observation = self.env["medical.observation"].create(
            {
                "name": "Observation 1",
                "reference_range_low": 2.5,
                "reference_range_high": 10.3,
                "patient_id": self.patient_1.id,
            }
        )
        observation.value_float = 5.3
        self.assertEqual(observation.interpretation, "normal")
        observation.value_float = 1.5
        self.assertEqual(observation.interpretation, "low")
        observation.value_float = 11.2
        self.assertEqual(observation.interpretation, "high")

    def test_compute_interpretation_int(self):
        observation = self.env["medical.observation"].create(
            {
                "name": "Observation 2",
                "reference_range_low": 2,
                "reference_range_high": 10,
                "patient_id": self.patient_1.id,
            }
        )
        observation.value_int = 5
        self.assertEqual(observation.interpretation, "normal")
        observation.value_int = 1
        self.assertEqual(observation.interpretation, "low")
        observation.value_int = 11
        self.assertEqual(observation.interpretation, "high")

    def test_compute_interpretation_bool(self):
        observation = self.env["medical.observation"].create(
            {"name": "Observation 3", "patient_id": self.patient_1.id}
        )
        observation.value_bool = True
        self.assertFalse(observation.interpretation)

    def test_compute_reference_range_with_range(self):
        uom = self.env.ref("medical_diagnostic_report.uom_gram_deciliter")
        observation = self.env["medical.observation"].create(
            {
                "name": "Observation 4",
                "reference_range_low": 2.5,
                "reference_range_high": 10.3,
                "uom_id": uom.id,
                "patient_id": self.patient_1.id,
            }
        )
        self.assertEqual(
            observation.reference_range_limit,
            "%.2f - %.2f"
            % (
                observation.reference_range_low,
                observation.reference_range_high,
            ),
        )

    def test_compute_reference_range_without_range(self):
        observation = self.env["medical.observation"].create(
            {"name": "Observation 5", "patient_id": self.patient_1.id}
        )
        self.assertFalse(observation.reference_range_limit)

    def test_compute_reference_range_only_high_reference_limit(self):
        uom = self.env.ref("medical_diagnostic_report.uom_gram_deciliter")
        observation = self.env["medical.observation"].create(
            {
                "name": "Observation 6",
                "reference_range_high": 10.3,
                "uom_id": uom.id,
                "patient_id": self.patient_1.id,
            }
        )
        self.assertEqual(
            observation.reference_range_limit,
            " ≤ {:.2f}".format(observation.reference_range_high),
        )
