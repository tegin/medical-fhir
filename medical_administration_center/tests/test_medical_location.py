# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestMedicalLocation(TransactionCase):
    def setUp(self):
        super().setUp()
        self.partner_obj = self.env["res.partner"].with_context(
            test_check_location_center=True
        )

    def test_center(self):
        vals = {
            "name": "location",
            "is_location": True,
        }
        with self.assertRaises(ValidationError):
            self.partner_obj.create(vals)
        center_vals = {
            "name": "test name",
            "is_center": True,
        }
        center = self.partner_obj.create(center_vals)
        self.assertTrue(center.is_center)
        vals["center_id"] = center.id
        self.assertEqual(center.location_count, 0)
        location = self.partner_obj.create(vals)
        self.assertTrue(location.is_location)
        self.assertEqual(center.location_count, 1)
