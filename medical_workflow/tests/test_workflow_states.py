# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestWorkflowStates(TransactionCase):

    def test_plan_definition(self):
        plan_obj = self.env['workflow.plan.definition']
        workflow_type = self.browse_ref('medical_workflow.medical_workflow')
        plan_1 = plan_obj.create({
            'name': 'P1',
            'type_id': workflow_type.id
        })
        self.assertFalse(plan_1.active)
        plan_1.activate()
        self.assertTrue(plan_1.active)
        plan_1.retire()
        self.assertFalse(plan_1.active)
        plan_1.reactivate()
        self.assertTrue(plan_1.active)

    def test_activity_definition(self):
        type = self.env['workflow.type'].create({
            'name': 'TEST',
            'model_id': self.browse_ref(
                'medical_administration.model_medical_patient').id,
            'model_ids': [(4, self.browse_ref(
                'medical_administration.model_medical_patient').id)],
        })
        activity = self.env['workflow.activity.definition'].create({
            'name': 'Activity',
            'type_id': type.id,
            'model_id': type.model_id.id
        })
        self.assertFalse(activity.active)
        activity.activate()
        self.assertTrue(activity.active)
        activity.retire()
        self.assertFalse(activity.active)
        activity.reactivate()
        self.assertTrue(activity.active)
