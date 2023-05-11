# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import logging
from datetime import date, datetime

import freezegun

from odoo.tests import TransactionCase

_logger = logging.getLogger(__name__)


class TestMedicalProcedureExternal(TransactionCase):
    def setUp(self):
        super(TestMedicalProcedureExternal, self).setUp()
        self.env.user.digital_signature = base64.b64encode(b"12345")
        self.patient_1 = self.env["medical.patient"].create(
            {"name": "Patient 1", "vat": "47238567H"}
        )
        self.encounter_1 = self.env["medical.encounter"].create(
            {"name": "Encounter 1", "patient_id": self.patient_1.id}
        )

        self.template_1 = self.env[
            "medical.procedure.external.request.template"
        ].create(
            {
                "name": "Template 1",
                "composition": "Everything is ok",
            }
        )
        self.template_2 = self.env[
            "medical.procedure.external.request.template"
        ].create(
            {
                "name": "Template 2",
                "composition": "Composition 2",
            }
        )
        self.template_3 = self.env[
            "medical.procedure.external.request.template"
        ].create(
            {
                "name": "Template 3",
                "composition": "Composition 3",
            }
        )
        report_generation = self.env[
            "medical.encounter.create.external.request"
        ].create(
            {
                "encounter_id": self.encounter_1.id,
                "template_id": self.template_1.id,
            }
        )
        action = report_generation.generate()
        self.report = self.env[action.get("res_model")].browse(
            action.get("res_id")
        )

    def test_finalization(self):
        self.assertNotEqual(self.report.fhir_state, "final")
        self.assertFalse(self.report.issued_date)
        self.assertFalse(self.report.issued_user_id)
        with freezegun.freeze_time("2020-01-01"):
            self.report.draft2final_action()
        self.assertEqual(self.report.fhir_state, "final")
        self.assertTrue(self.report.issued_date)
        self.assertEqual(
            self.report.issued_date, datetime(2020, 1, 1, 0, 0, 0)
        )
        self.assertTrue(self.report.issued_user_id)
        self.assertEqual(self.report.issued_user_id, self.env.user)

        self.assertTrue(self.report.issued_user_id.digital_signature)
        self.assertEqual(
            self.report.issued_user_id.digital_signature,
            self.env.user.digital_signature,
        )

    def test_cancellation(self):
        self.assertNotEqual(self.report.fhir_state, "cancelled")
        self.assertFalse(self.report.cancel_date)
        self.assertFalse(self.report.cancel_user_id)
        with freezegun.freeze_time("2020-01-01"):
            self.report.cancel_action()
        self.assertEqual(self.report.fhir_state, "cancelled")
        self.assertTrue(self.report.cancel_date)
        self.assertEqual(
            self.report.cancel_date, datetime(2020, 1, 1, 0, 0, 0)
        )
        self.assertTrue(self.report.cancel_user_id)
        self.assertEqual(self.report.cancel_user_id, self.env.user)

    def test_age(self):
        self.patient_1.write({"birth_date": date(2002, 1, 1)})
        with freezegun.freeze_time("2020-01-01"):
            self.assertEqual(
                18,
                self.env[
                    "medical.procedure.external.request.template"
                ]._compute_age(self.patient_1),
            )
        with freezegun.freeze_time("2019-12-31"):
            self.assertEqual(
                17,
                self.env[
                    "medical.procedure.external.request.template"
                ]._compute_age(self.patient_1),
            )

    def test_report_generation(self):
        report_generation = self.env[
            "medical.encounter.create.external.request"
        ].create(
            {
                "encounter_id": self.encounter_1.id,
                "template_id": self.template_1.id,
            }
        )
        self.assertEqual(self.encounter_1.external_request_count, 1)
        action = report_generation.generate()
        report = self.env[action.get("res_model")].browse(action.get("res_id"))
        self.assertEqual(self.encounter_1.external_request_count, 2)
        self.assertEqual("medical.procedure.external.request", report._name)
        self.assertEqual(self.encounter_1, report.encounter_id)
        self.assertEqual(self.patient_1, report.patient_id)
        self.assertEqual(self.patient_1.name, report.patient_id.name)
        self.assertEqual(self.patient_1.vat, report.patient_id.vat)
        self.assertEqual(self.template_1.name, report.name)
        self.assertEqual(self.template_1.composition, report.composition)

    def test_encounter_button(self):
        action = self.encounter_1.action_view_external_request()
        reports = self.env[action["res_model"]].search(action["domain"])
        self.assertIn(self.report, reports)
