# Copyright 2022 Creu Blanca

from odoo.tests.common import TransactionCase


class TestMedicalPatient(TransactionCase):
    def setUp(self):
        super(TestMedicalPatient, self).setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id}
        )
        self.external_product_request_order = self.env[
            "medical.product.request.order"
        ].create(
            {
                "category": "discharge",
                "patient_id": self.patient.id,
            }
        )
        self.internal_product_request_order = self.env[
            "medical.product.request.order"
        ].create(
            {
                "category": "inpatient",
                "patient_id": self.patient.id,
            }
        )

    def test_create_medical_product_request(self):
        action = self.patient.with_context(
            {"default_category": "discharge"}
        ).create_medical_product_request_order()
        self.assertEqual(action["res_model"], "medical.product.request.order")
        self.assertEqual(
            action["context"]["default_encounter_id"], self.encounter.id
        )
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )
        self.assertEqual(action["context"]["default_category"], "discharge")

    def test_action_view_external_medical_product_request_order_ids(self):
        self.assertEqual(self.patient.external_product_request_order_count, 1)
        action = (
            self.patient.action_view_external_medical_product_request_order_ids()
        )
        self.assertEqual(
            action["res_id"], self.external_product_request_order.id
        )
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )
        self.assertEqual(
            action["context"]["default_encounter_id"], self.encounter.id
        )
        self.assertEqual(action["context"]["default_category"], "discharge")

    def test_action_view_internal_medical_product_request_order_ids(self):
        self.assertEqual(self.patient.internal_product_request_order_count, 1)
        action = (
            self.patient.action_view_internal_medical_product_request_order_ids()
        )
        self.assertEqual(
            action["res_id"], self.internal_product_request_order.id
        )
        self.assertEqual(
            action["context"]["default_patient_id"], self.patient.id
        )
        self.assertEqual(
            action["context"]["default_encounter_id"], self.encounter.id
        )
        self.assertEqual(action["context"]["default_category"], "inpatient")
