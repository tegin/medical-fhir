# Copyright 2022 CreuBlanca
# Copyright 2022 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from psycopg2.errors import UniqueViolation

from odoo import fields
from odoo.tests import TransactionCase
from odoo.tools import mute_logger


class TestMedicalPatient(TransactionCase):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()
        cls.patient = cls.env["medical.patient"].create({"name": "Test Patient"})
        return res

    def test_internal_identifier(self):
        self.assertTrue(self.patient.internal_identifier)
        self.assertNotEqual(self.patient.internal_identifier, "/")

    def test_deceased(self):
        self.patient.birth_date = fields.Date.today()
        self.patient.deceased_date = fields.Date.today()
        self.assertTrue(self.patient.is_deceased)

    def test_patient_link_partner(self):
        """Associate an existing partner for a patient"""
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.assertFalse(self.patient.partner_ids)
        self.env["patient.partner.search"].create(
            {
                "patient_id": self.patient.id,
                "partner_id": partner.id,
                "partner_type": "f",
            }
        ).add_contact()
        self.assertTrue(self.patient.partner_ids)
        self.assertEqual(self.patient.partner_ids.partner_id, partner)

    def test_add_existing_partner(self):
        """Get error when trying add existing partner
        who is already added as contact for a patient"""
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.env["patient.partner.search"].create(
            {
                "patient_id": self.patient.id,
                "partner_id": partner.id,
                "partner_type": "f",
            }
        ).add_contact()

        with self.assertRaisesRegex(
            UniqueViolation, r"medical_patient_partner_partner_uniq"
        ):
            with mute_logger("odoo.sql_db"):
                self.env["patient.partner.search"].create(
                    {
                        "patient_id": self.patient.id,
                        "partner_id": partner.id,
                        "partner_type": "f",
                    }
                ).add_contact()
