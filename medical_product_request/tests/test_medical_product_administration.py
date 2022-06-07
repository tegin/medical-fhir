# Copyright 2022 Creu Blanca

from datetime import datetime

import freezegun
from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestMedicalProductAdministration(TransactionCase):
    def setUp(self):
        super(TestMedicalProductAdministration, self).setUp()

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
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.encounter = self.env["medical.encounter"].create(
            {"patient_id": self.patient.id}
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

        self.administration = self.env[
            "medical.product.administration"
        ].create(
            {
                "product_request_id": self.internal_product_request.id,
                "quantity_administered": 1,
                "medical_product_template_id": self.medical_product_ibuprofen_template.id,
                "quantity_administered_uom_id": self.tablet_uom.id,
            }
        )

    def test_complete_administration_action(self):
        with freezegun.freeze_time("2022-01-01"):
            self.administration.complete_administration_action()
        self.assertEqual(self.administration.state, "completed")
        self.assertEqual(
            self.administration.administration_date,
            datetime(2022, 1, 1, 0, 0, 0),
        )
        self.assertEqual(
            self.administration.administration_user_id.id, self.env.user.id
        )

    def test_cancel_action(self):
        with freezegun.freeze_time("2022-01-01"):
            self.administration.cancel_action()
        self.assertEqual(self.administration.state, "cancelled")
        self.assertEqual(
            self.administration.cancel_date, datetime(2022, 1, 1, 0, 0, 0)
        )
        self.assertEqual(
            self.administration.cancel_user_id.id, self.env.user.id
        )

    def test_check_quantity_administered(self):
        with self.assertRaises(ValidationError):
            self.env["medical.product.administration"].create(
                {
                    "product_request_id": self.internal_product_request.id,
                    "quantity_administered": 0,
                    "quantity_administered_uom_id": self.tablet_uom.id,
                }
            )

    def test_compute_quantity_uom_domain(self):
        self.assertRegex(
            self.administration.quantity_uom_domain, "%s" % self.tablet_uom.id
        )
        self.administration.medical_product_template_id = False
        self.assertRegex(self.administration.quantity_uom_domain, "%s" % 0)
