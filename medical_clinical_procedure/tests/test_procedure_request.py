# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import UserError, Warning as Warn
from odoo.tests import TransactionCase


class TestProcedureRequest(TransactionCase):
    def setUp(self):
        res = super(TestProcedureRequest, self).setUp()
        self.patient = self.browse_ref("medical_base.patient_01")
        self.plan = self.browse_ref("medical_workflow.mr_knee")
        return res

    def test_procedure(self):
        procedure_requests = self.env["medical.procedure.request"].search(
            [("patient_id", "=", self.patient.id)]
        )
        self.assertEqual(len(procedure_requests), 0)
        self.env["medical.add.plan.definition"].create(
            {"patient_id": self.patient.id, "plan_definition_id": self.plan.id}
        ).run()
        procedure_requests = self.env["medical.procedure.request"].search(
            [("patient_id", "=", self.patient.id)]
        )
        self.assertGreater(len(procedure_requests), 0)
        self.env["procedure.request.make.procedure"].with_context(
            active_ids=procedure_requests.ids
        ).create({}).make_procedure()
        procedures = self.env["medical.procedure"].search(
            [("procedure_request_id", "in", procedure_requests.ids)]
        )
        self.assertEqual(len(procedure_requests), len(procedures))
        with self.assertRaises(UserError):
            self.env["procedure.request.make.procedure"].with_context(
                active_ids=procedure_requests.ids
            ).create({}).make_procedure()
        for request in procedure_requests:
            self.assertEqual(request.procedure_count, 1)
            with self.assertRaises(Warn):
                request.unlink()
            action = request.action_view_procedure()
            self.assertEqual(
                action["context"]["default_procedure_request_id"], request.id
            )

    def test_procedure_request_workflow(self):
        request = self.env["medical.procedure.request"].create(
            {"patient_id": self.patient.id}
        )
        self.assertNotEqual(request.internal_identifier, "/")
        procedure = request.generate_event()
        self.assertEqual(procedure.procedure_request_id.id, request.id)
        self.assertEqual(request.fhir_state, "draft")
        request.draft2active()
        self.assertEqual(request.fhir_state, "active")
        request.active2suspended()
        self.assertEqual(request.fhir_state, "suspended")
        request.reactive()
        request.active2error()
        self.assertEqual(request.fhir_state, "entered-in-error")
        request.reactive()
        request.active2completed()
        self.assertEqual(request.fhir_state, "completed")
        request.reactive()
        request.cancel()
        self.assertEqual(request.fhir_state, "cancelled")
