# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestCondition(TransactionCase):
    def setUp(self):
        super(TestCondition, self).setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.finding = self.env["medical.clinical.finding"].create(
            {"name": "Finding"}
        )

    def test_conditions(self):
        self.assertEqual(self.patient.medical_condition_count, 0)
        self.env["medical.condition"].create(
            {
                "patient_id": self.patient.id,
                "clinical_finding_id": self.finding.id,
            }
        )
        self.assertEqual(self.patient.medical_condition_count, 1)
        res = self.patient.action_view_medical_conditions()
        self.assertEqual(res["context"]["default_patient_id"], self.patient.id)
