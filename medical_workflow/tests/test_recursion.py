# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestRecursion(TransactionCase):
    def test_recursion(self):
        plan_obj = self.env["workflow.plan.definition"]
        action_obj = self.env["workflow.plan.definition.action"]
        plan_1 = plan_obj.create({"name": "P1"})
        with self.assertRaises(UserError):
            action_obj.create(
                {
                    "direct_plan_definition_id": plan_1.id,
                    "name": plan_1.name,
                    "execute_plan_definition_id": plan_1.id,
                }
            )
        plan_2 = plan_obj.create({"name": "P2"})
        action_obj.create(
            {
                "direct_plan_definition_id": plan_1.id,
                "name": plan_2.name,
                "execute_plan_definition_id": plan_2.id,
            }
        )
        with self.assertRaises(UserError):
            action_obj.create(
                {
                    "direct_plan_definition_id": plan_2.id,
                    "name": plan_1.name,
                    "execute_plan_definition_id": plan_1.id,
                }
            )
        plan_3 = plan_obj.create({"name": "P3"})
        action_obj.create(
            {
                "direct_plan_definition_id": plan_2.id,
                "name": plan_3.name,
                "execute_plan_definition_id": plan_3.id,
            }
        )
        with self.assertRaises(UserError):
            action_obj.create(
                {
                    "direct_plan_definition_id": plan_3.id,
                    "name": plan_1.name,
                    "execute_plan_definition_id": plan_1.id,
                }
            )
        action = action_obj.create(
            {"direct_plan_definition_id": plan_1.id, "name": "AUX"}
        )
        with self.assertRaises(UserError):
            action_obj.create(
                {
                    "parent_id": action.id,
                    "name": plan_1.name,
                    "execute_plan_definition_id": plan_1.id,
                }
            )
