# Copyright 2017 ForgeFlow Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestWorkflowStates(TransactionCase):
    def test_plan_definition(self):
        plan_obj = self.env["workflow.plan.definition"]
        plan_1 = plan_obj.create({"name": "P1"})
        self.assertFalse(plan_1.active)
        plan_1.activate()
        self.assertTrue(plan_1.active)
        plan_1.retire()
        self.assertFalse(plan_1.active)
        plan_1.reactivate()
        self.assertTrue(plan_1.active)

    def test_activity_definition(self):
        activity = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity",
                "model_id": self.browse_ref("medical_base.model_medical_patient").id,
            }
        )
        self.assertFalse(activity.active)
        activity.activate()
        self.assertTrue(activity.active)
        activity.retire()
        self.assertFalse(activity.active)
        activity.reactivate()
        self.assertTrue(activity.active)
