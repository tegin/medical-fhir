# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import TransactionCase


class TestProcedure(TransactionCase):
    def setUp(self):
        res = super(TestProcedure, self).setUp()
        self.patient = self.browse_ref("medical_base.patient_01")
        self.plan = self.browse_ref("medical_workflow.mr_knee")
        return res

    def open_procedure(self):
        procedure = self.env["medical.procedure"].create(
            {"patient_id": self.patient.id}
        )
        self.assertEqual(procedure.fhir_state, "preparation")
        procedure.preparation2in_progress()
        self.assertEqual(procedure.fhir_state, "in-progress")
        self.assertTrue(procedure.performed_initial_date)
        return procedure

    def test_procedure_completed_flow(self):
        procedure = self.open_procedure()
        procedure.in_progress2suspended()
        self.assertEqual(procedure.fhir_state, "suspended")
        procedure.suspended2in_progress()
        self.assertEqual(procedure.fhir_state, "in-progress")
        procedure.in_progress2completed()
        self.assertEqual(procedure.fhir_state, "completed")
        self.assertTrue(procedure.performed_end_date)

    def test_procedure_aborted_flow(self):
        procedure = self.open_procedure()
        procedure.in_progress2aborted()
        self.assertEqual(procedure.fhir_state, "aborted")
