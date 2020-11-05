# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMedicalRequest(TransactionCase):
    def setUp(self):
        super(TestMedicalRequest, self).setUp()
        self.patient = self.env["medical.patient"].create(
            {"name": "Test Patient"}
        )
        self.patient2 = self.env["medical.patient"].create(
            {"name": "Test Patient2"}
        )

    def test_constrains(self):
        request = self.env["medical.request.group"].create(
            {"patient_id": self.patient.id}
        )
        with self.assertRaises(ValidationError):
            self.env["medical.request.group"].create(
                {
                    "patient_id": self.patient2.id,
                    "request_group_id": request.id,
                }
            )

    def test_views(self):
        procedure = self.env["medical.request.group"].create(
            {"patient_id": self.patient.id}
        )
        procedure._compute_request_group_ids()
        self.assertEqual(procedure.request_group_count, 0)
        procedure.with_context(
            inverse_id="active_id", model_name="medical.request.group"
        ).action_view_request()
        # 1 procedure
        procedure2 = self.env["medical.request.group"].create(
            {"patient_id": self.patient.id, "request_group_id": procedure.id}
        )
        procedure._compute_request_group_ids()
        self.assertEqual(procedure.request_group_ids.ids, [procedure2.id])
        self.assertEqual(procedure.request_group_count, 1)
        procedure.with_context(
            inverse_id="active_id", model_name="medical.request.group"
        ).action_view_request()
        # 2 procedure
        procedure3 = self.env["medical.request.group"].create(
            {"patient_id": self.patient.id, "request_group_id": procedure.id}
        )
        procedure._compute_request_group_ids()
        self.assertEqual(procedure.request_group_count, 2)
        self.assertEqual(
            procedure.request_group_ids.ids.sort(),
            [procedure2.id, procedure3.id].sort(),
        )
        procedure.with_context(
            inverse_id="active_id", model_name="medical.request.group"
        ).action_view_request()
