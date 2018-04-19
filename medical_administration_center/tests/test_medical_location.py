# Copyright 2017 LasLabs Inc.
# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestMedicalLocation(TransactionCase):

    def test_location(self):
        center_vals = {
            'name': 'test name',
            'description': 'test description',
            'is_center': True,
        }
        center = self.env['res.partner'].create(center_vals)
        self.assertTrue(center.is_center)
