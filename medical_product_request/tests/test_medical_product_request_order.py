# Copyright 2022 Creu Blanca

from datetime import datetime

import freezegun
from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestMedicalProductRequestOrder(TransactionCase):
    def setUp(self):
        super(TestMedicalProductRequestOrder, self).setUp()

        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id}
        )
        self.tablet_uom = self.env["uom.uom"].create(
            {
                "name": "Tablets",
                "category_id": self.env.ref("uom.product_uom_categ_unit").id,
                "factor": 1.0,
                "uom_type": "bigger",
                "rounding": 0.001,
            }
        )
        self.tablet_form = self.env["medication.form"].create(
            {
                "name": "EFG film coated tablets",
                "uom_ids": [(4, self.tablet_uom.id)],
            }
        )
        self.medical_product_ibuprofen_template = self.env[
            "medical.product.template"
        ].create(
            {
                "name": "Ibuprofen",
                "product_type": "medication",
                "ingredients": "Ibuprofen",
                "dosage": "600 mg",
                "form_id": self.tablet_form.id,
            }
        )
        self.medical_product_ibuprofen_30_tablets = self.env[
            "medical.product.product"
        ].create(
            {
                "product_tmpl_id": self.medical_product_ibuprofen_template.id,
                "amount": 30,
                "amount_uom_id": self.tablet_uom.id,
            }
        )
        self.external_product_request_order = self.env[
            "medical.product.request.order"
        ].create(
            {
                "category": "discharge",
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
            }
        )
        self.external_product_request = self.env[
            "medical.product.request"
        ].create(
            {
                "request_order_id": self.external_product_request_order.id,
                "medical_product_template_id": self.medical_product_ibuprofen_template.id,
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "rate_quantity": 3,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 60,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )
        self.internal_product_request_order = self.env[
            "medical.product.request.order"
        ].create(
            {
                "category": "inpatient",
                "patient_id": self.patient.id,
                "encounter_id": self.encounter.id,
            }
        )
        self.internal_product_request = self.env[
            "medical.product.request"
        ].create(
            {
                "request_order_id": self.internal_product_request_order.id,
                "medical_product_template_id": self.medical_product_ibuprofen_template.id,
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "rate_quantity": 3,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 5,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )

    def test_validate_action_without_product_request_ids(self):
        product_request_order = self.env[
            "medical.product.request.order"
        ].create(
            {
                "category": "discharge",
                "patient_id": self.patient.id,
            }
        )
        with self.assertRaises(ValidationError):
            product_request_order.validate_action()

    def test_validate_action_discharge_order(self):
        self.assertEqual(self.external_product_request_order.state, "draft")
        with freezegun.freeze_time("2022-01-01"):
            self.external_product_request_order.validate_action()
        self.assertEqual(
            self.external_product_request_order.state, "completed"
        )
        self.assertFalse(self.external_product_request_order.can_administrate)
        self.assertEqual(
            self.external_product_request_order.validation_date,
            datetime(2022, 1, 1, 0, 0, 0),
        )
        self.assertEqual(
            self.external_product_request_order.requester_id.id,
            self.env.user.id,
        )
        for request in self.external_product_request_order.product_request_ids:
            self.assertEqual(request.state, "completed")
            self.assertFalse(request.can_administrate)
            self.assertEqual(
                request.validation_date, datetime(2022, 1, 1, 0, 0, 0)
            )
            self.assertEqual(request.requester_id.id, self.env.user.id)

    def test_validate_action_inpatient_order(self):
        self.assertEqual(self.internal_product_request_order.state, "draft")
        self.assertFalse(self.internal_product_request_order.can_administrate)
        with freezegun.freeze_time("2022-01-01"):
            self.internal_product_request_order.validate_action()
        self.assertEqual(self.internal_product_request_order.state, "active")
        self.assertTrue(self.internal_product_request_order.can_administrate)
        self.assertEqual(
            self.internal_product_request_order.validation_date,
            datetime(2022, 1, 1, 0, 0, 0),
        )
        self.assertEqual(
            self.internal_product_request_order.requester_id.id,
            self.env.user.id,
        )
        for request in self.internal_product_request_order.product_request_ids:
            self.assertEqual(request.state, "active")
            self.assertTrue(request.can_administrate)
            self.assertEqual(
                request.validation_date, datetime(2022, 1, 1, 0, 0, 0)
            )
            self.assertEqual(request.requester_id.id, self.env.user.id)

    def test_cancel_action(self):
        self.assertEqual(self.internal_product_request_order.state, "draft")
        self.assertFalse(self.internal_product_request_order.can_administrate)
        with freezegun.freeze_time("2022-01-01"):
            self.internal_product_request_order.cancel_action()
        self.assertEqual(
            self.internal_product_request_order.state, "cancelled"
        )
        self.assertFalse(self.internal_product_request_order.can_administrate)
        self.assertEqual(
            self.internal_product_request_order.cancel_date,
            datetime(2022, 1, 1, 0, 0, 0),
        )
        self.assertEqual(
            self.internal_product_request_order.cancel_user_id.id,
            self.env.user.id,
        )
        for request in self.internal_product_request_order.product_request_ids:
            self.assertEqual(request.state, "cancelled")
            self.assertFalse(request.can_administrate)
            self.assertEqual(
                request.cancel_date, datetime(2022, 1, 1, 0, 0, 0)
            )
            self.assertEqual(request.cancel_user_id.id, self.env.user.id)

    def test_compute_medical_product_template_ids(self):
        self.assertEqual(
            len(
                self.internal_product_request_order.medical_product_template_ids
            ),
            1,
        )
        self.assertEqual(
            self.internal_product_request_order.medical_product_template_ids[
                0
            ].id,
            self.medical_product_ibuprofen_template.id,
        )

    def test_get_last_encounter_or_false(self):
        patient = self.env["medical.patient"].create({"name": "Patient"})
        product_request_order_1 = self.env[
            "medical.product.request.order"
        ].create(
            {
                "category": "discharge",
                "patient_id": patient.id,
            }
        )
        self.assertFalse(product_request_order_1.encounter_id)
        encounter = self.env["medical.encounter"].create(
            {"patient_id": patient.id}
        )
        patient.refresh()
        product_request_order_2 = self.env[
            "medical.product.request.order"
        ].create(
            {
                "category": "discharge",
                "patient_id": patient.id,
            }
        )
        product_request_order_2.refresh()
        self.assertEqual(product_request_order_2.encounter_id.id, encounter.id)

    def test_onchange_encounter_date(self):
        with freezegun.freeze_time("2022-01-01"):
            encounter_1 = self.env["medical.encounter"].create(
                {"patient_id": self.patient.id, "create_date": datetime.now()}
            )
        with freezegun.freeze_time("2022-02-01"):
            encounter_2 = self.env["medical.encounter"].create(
                {"patient_id": self.patient.id, "create_date": datetime.now()}
            )
        with freezegun.freeze_time("2022-02-02"):
            request_order = self.env["medical.product.request.order"].create(
                {
                    "category": "discharge",
                    "patient_id": self.patient.id,
                    "create_date": datetime.now(),
                }
            )
            with Form(request_order) as order:
                self.assertFalse(order.show_encounter_warning)
                order.encounter_id = encounter_1
                self.assertTrue(order.show_encounter_warning)
                order.encounter_id = self.env["medical.encounter"]
                self.assertFalse(order.show_encounter_warning)
                order.encounter_id = encounter_2
                self.assertFalse(order.show_encounter_warning)
                order.encounter_id = self.env["medical.encounter"]
