# Copyright 2022 Creu Blanca

from datetime import datetime

import freezegun
from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase


class TestMedicalProductRequest(TransactionCase):
    def setUp(self):
        super(TestMedicalProductRequest, self).setUp()
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
        self.medical_product_ibuprofen_60_tablets = self.env[
            "medical.product.product"
        ].create(
            {
                "product_tmpl_id": self.medical_product_ibuprofen_template.id,
                "amount": 60,
                "amount_uom_id": self.tablet_uom.id,
            }
        )

        self.medical_product_crutch_template = self.env[
            "medical.product.template"
        ].create(
            {
                "name": "crutch",
                "product_type": "device",
            }
        )
        self.medical_product_crutch = self.env[
            "medical.product.product"
        ].create(
            {
                "product_tmpl_id": self.medical_product_crutch_template.id,
                "amount": 1,
                "amount_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )

        self.ml_uom = self.env["uom.uom"].create(
            {
                "name": "ml",
                "category_id": self.env.ref("uom.product_uom_categ_vol").id,
                "factor": 1000,
                "uom_type": "smaller",
                "rounding": 0.001,
            }
        )

        self.drops_uom = self.env["uom.uom"].create(
            {
                "name": "Drops",
                "category_id": self.env.ref("uom.product_uom_categ_vol").id,
                "factor": 20000,
                "uom_type": "smaller",
                "rounding": 0.001,
            }
        )
        self.solution_form = self.env["medication.form"].create(
            {
                "name": "Eye drops in solution",
                "uom_ids": [(4, self.ml_uom.id), (4, self.drops_uom.id)],
            }
        )

        self.medical_product_acular_template = self.env[
            "medical.product.template"
        ].create(
            {
                "name": "Acular",
                "product_type": "medication",
                "ingredients": "Ketorolac tromethamol",
                "dosage": "5 mg/ml",
                "form_id": self.solution_form.id,
            }
        )
        self.medical_product_acular_5_ml = self.env[
            "medical.product.product"
        ].create(
            {
                "product_tmpl_id": self.medical_product_acular_template.id,
                "amount": 5,
                "amount_uom_id": self.ml_uom.id,
            }
        )
        self.medical_product_acular_10_ml = self.env[
            "medical.product.product"
        ].create(
            {
                "product_tmpl_id": self.medical_product_acular_template.id,
                "amount": 10,
                "amount_uom_id": self.ml_uom.id,
            }
        )

    def test_compute_medical_product_id_internal_request(self):
        request = self.env["medical.product.request"].create(
            {
                "medical_product_template_id": self.medical_product_ibuprofen_template.id,
                "category": "inpatient",
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "rate_quantity": 3,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 60,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )
        self.assertFalse(request.medical_product_id)
        self.assertEqual(request.quantity_to_dispense, 0)

    def test_compute_medical_product_id_device(self):
        request = self.env["medical.product.request"].create(
            {
                "medical_product_template_id": self.medical_product_crutch_template.id,
                "category": "discharge",
                "dose_quantity": 1,
                "dose_uom_id": self.env.ref("uom.product_uom_unit").id,
            }
        )
        self.assertEqual(
            request.medical_product_id.id, self.medical_product_crutch.id
        )
        self.assertEqual(request.quantity_to_dispense, 1)

    def test_compute_medical_product_id_medication_tablet_form(self):
        request = self.env["medical.product.request"].create(
            {
                "medical_product_template_id": self.medical_product_ibuprofen_template.id,
                "category": "discharge",
                "dose_quantity": 1,
                "dose_uom_id": self.tablet_uom.id,
                "rate_quantity": 1,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 30,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )
        self.assertEqual(
            request.medical_product_id.id,
            self.medical_product_ibuprofen_30_tablets.id,
        )
        self.assertEqual(request.quantity_to_dispense, 1)
        request.duration = 40
        self.assertEqual(
            request.medical_product_id.id,
            self.medical_product_ibuprofen_60_tablets.id,
        )
        self.assertEqual(request.quantity_to_dispense, 1)
        request.duration = 80
        self.assertEqual(
            request.medical_product_id.id,
            self.medical_product_ibuprofen_60_tablets.id,
        )
        self.assertEqual(request.quantity_to_dispense, 2)

    def test_compute_medical_product_id_medication_solution_form(self):
        request = self.env["medical.product.request"].create(
            {
                "medical_product_template_id": self.medical_product_acular_template.id,
                "category": "discharge",
                "dose_quantity": 3,
                "dose_uom_id": self.drops_uom.id,
                "rate_quantity": 2,
                "rate_uom_id": self.env.ref("uom.product_uom_day").id,
                "duration": 10,
                "duration_uom_id": self.env.ref("uom.product_uom_day").id,
            }
        )

        # We consider that a drop is equal to 0,05 ml
        # total_dose = 3 drops * 0,05 ml/ 1 drop *  2 drops/day * 10 days = 3 ml
        self.assertEqual(
            request.medical_product_id.id, self.medical_product_acular_5_ml.id
        )
        self.assertEqual(request.quantity_to_dispense, 1)
        request.duration = 30
        self.assertEqual(
            request.medical_product_id.id, self.medical_product_acular_10_ml.id
        )
        self.assertEqual(request.quantity_to_dispense, 1)
        request.duration = 100
        self.assertEqual(
            request.medical_product_id.id, self.medical_product_acular_10_ml.id
        )
        self.assertEqual(request.quantity_to_dispense, 3)
