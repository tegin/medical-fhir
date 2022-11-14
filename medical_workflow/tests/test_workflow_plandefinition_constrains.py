# Copyright 2017 ForgeFlow Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestWorkflowPlandefinition(TransactionCase):
    def setUp(self):
        res = super(TestWorkflowPlandefinition, self).setUp()
        self.activity = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity",
            }
        )
        self.plan = self.env["workflow.plan.definition"].create(
            {"name": "Plan"}
        )
        self.plan.activate()
        self.activity_2 = self.env["workflow.activity.definition"].create(
            {
                "name": "Activity 2",
            }
        )
        self.plan_2 = self.env["workflow.plan.definition"].create(
            {"name": "Plan 2"}
        )
        return res

    def test_show_plan(self):
        plan_action = self.activity.action_show_plans()
        self.assertFalse(
            self.env[plan_action["res_model"]].search(plan_action["domain"])
        )
        self.env["workflow.plan.definition.action"].create(
            {
                "name": "Action",
                "direct_plan_definition_id": self.plan.id,
                "activity_definition_id": self.activity.id,
            }
        )
        plan_action = self.activity.action_show_plans()
        self.assertEqual(
            self.plan,
            self.env[plan_action["res_model"]].search(plan_action["domain"]),
        )

    def test_action(self):
        action = self.env["workflow.plan.definition.action"].new(
            {
                "name": "Action",
                "direct_plan_definition_id": self.plan.id,
                "activity_definition_id": self.activity.id,
            }
        )
        action.plan_definition_id = self.plan_2
        action._onchange_activity_definition_id()
        action.activity_definition_id = self.activity_2
        action._onchange_activity_definition_id()
        self.assertEqual(action.name, self.activity_2.name)

    def test_action_constrain(self):
        action = self.env["workflow.plan.definition.action"].create(
            {
                "name": "Action",
                "direct_plan_definition_id": self.plan.id,
                "activity_definition_id": self.activity.id,
            }
        )
        with self.assertRaises(UserError):
            action.parent_id = action
        action2 = self.env["workflow.plan.definition.action"].create(
            {"name": "Action", "direct_plan_definition_id": self.plan.id}
        )
        with self.assertRaises(ValidationError):
            action2.execute_plan_definition_id = False
            action2.activity_definition_id = False

    def test_add_plan_definition_on_patients(self):
        plan_obj = self.env["workflow.plan.definition"]
        wzd = self.env["medical.add.plan.definition"]
        patient = self.browse_ref("medical_base.patient_01")
        plan_1 = plan_obj.create({"name": "P1"})
        wzd_1 = wzd.create(
            {"patient_id": patient.id, "plan_definition_id": plan_1.id}
        )
        with self.assertRaises(UserError):
            wzd_1.run()

    def test_execute_plan_definition(self):
        plan_obj = self.env["workflow.plan.definition"]
        patient = self.browse_ref("medical_base.patient_01")
        plan_1 = plan_obj.create({"name": "P1"})
        plan_1.execute_plan_definition({"patient_id": patient.id})
