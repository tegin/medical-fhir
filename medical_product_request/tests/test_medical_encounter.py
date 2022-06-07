# Copyright 2022 Creu Blanca

from datetime import datetime

import freezegun
from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestMedicalEncounter(TransactionCase):
    def setUp(self):
        super(TestMedicalEncounter, self).setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id}
        )
        self.external_product_request_order = self.env[
            "medical.product.request.order"
        ].create(
            {
                "category": "discharge",
                "encounter_id": self.encounter.id,
                "patient_id": self.patient.id,
            }
        )
        self.internal_product_request_order = self.env[
            "medical.product.request.order"
        ].create(
            {
                "category": "inpatient",
                "encounter_id": self.encounter.id,
                "patient_id": self.patient.id,
            }
        )

    def test_create_medical_product_request(self):
        action = self.encounter.with_context(
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
        self.assertEqual(
            self.encounter.external_product_request_order_count, 1
        )
        action = (
            self.encounter.action_view_external_medical_product_request_order_ids()
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
        self.assertEqual(
            self.encounter.internal_product_request_order_count, 1
        )
        action = (
            self.encounter.action_view_internal_medical_product_request_order_ids()
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
