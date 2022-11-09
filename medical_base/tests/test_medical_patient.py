# Copyright 2022 CreuBlanca
# Copyright 2022 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields
from odoo.tests import TransactionCase


class TestMedicalPatient(TransactionCase):
    def test_creation(self):
        patient = self.env["medical.patient"].create({"name": "Test Patient"})
        self.assertTrue(patient.internal_identifier)
        self.assertNotEqual(patient.internal_identifier, "/")
        patient.birth_date = fields.Date.today()
        patient.deceased_date = fields.Date.today()
        self.assertTrue(patient.is_deceased)
