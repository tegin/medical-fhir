# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMedicalRequest(TransactionCase):
    def setUp(self):
        super(TestMedicalRequest, self).setUp()
        self.patient = self.env['medical.patient'].create({
            'name': 'Test Patient'
        })
        self.patient2 = self.env['medical.patient'].create({
            'name': 'Test Patient2'
        })

    def test_constrains(self):
        careplan = self.env['medical.careplan'].create({
            'patient_id': self.patient.id
        })
        with self.assertRaises(ValidationError):
            self.env['medical.careplan'].create({
                'patient_id': self.patient2.id,
                'careplan_id': careplan.id,
            })

    def test_views(self):
        careplan = self.env['medical.careplan'].create({
            'patient_id': self.patient.id
        })
        careplan._compute_careplan_ids()
        self.assertEqual(careplan.careplan_count, 0)
        careplan.with_context(
            inverse_id='active_id', model_name='medical.careplan')\
            .action_view_request()
        # 1 care plan
        careplan2 = self.env['medical.careplan'].create({
            'patient_id': self.patient.id,
            'careplan_id': careplan.id,
        })
        careplan._compute_careplan_ids()
        self.assertEqual(careplan.careplan_ids.ids, [careplan2.id])
        self.assertEqual(careplan.careplan_count, 1)
        careplan.with_context(
            inverse_id='active_id', model_name='medical.careplan')\
            .action_view_request()
        # 2 care plans
        careplan3 = self.env['medical.careplan'].create({
            'patient_id': self.patient.id,
            'careplan_id': careplan.id,
        })
        careplan._compute_careplan_ids()
        self.assertEqual(careplan.careplan_count, 2)
        self.assertEqual(
            careplan.careplan_ids.ids.sort(),
            [careplan2.id, careplan3.id].sort())
        careplan.with_context(
            inverse_id='active_id', model_name='medical.careplan')\
            .action_view_request()
