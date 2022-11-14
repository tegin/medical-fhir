# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import TransactionCase


class TestCareplan(TransactionCase):
    def setUp(self):
        res = super(TestCareplan, self).setUp()
        self.patient = self.env["medical.patient"].create(
            {"name": "Test Patient"}
        )
        self.plan = self.browse_ref("medical_workflow.mr_knee")
        return res

    def test_careplan_workflow(self):
        request = self.env["medical.careplan"].create(
            {"patient_id": self.patient.id}
        )
        self.assertNotEqual(request.internal_identifier, "/")
        self.assertEqual(request.fhir_state, "draft")
        self.assertFalse(request.start_date)
        request.draft2active()
        self.assertTrue(request.start_date)
        self.assertEqual(request.fhir_state, "active")
        request.active2suspended()
        self.assertEqual(request.fhir_state, "suspended")
        request.reactive()
        request.active2error()
        self.assertEqual(request.fhir_state, "entered-in-error")
        request.reactive()
        self.assertFalse(request.end_date)
        request.active2completed()
        self.assertEqual(request.fhir_state, "completed")
        self.assertTrue(request.end_date)
        request.reactive()
        request.cancel()
        self.assertEqual(request.fhir_state, "cancelled")
        inverse_name = request._get_parent_field_name()
        self.assertEqual(inverse_name, "careplan_id")
