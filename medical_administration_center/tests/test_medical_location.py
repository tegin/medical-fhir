# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestMedicalLocation(TransactionCase):
    def test_center(self):
        vals = {
            "name": "location",
            "description": "location_description",
            "is_location": True,
        }
        with self.assertRaises(ValidationError):
            self.env["res.partner"].create(vals)
        center_vals = {
            "name": "test name",
            "description": "test description",
            "is_center": True,
        }
        center = self.env["res.partner"].create(center_vals)
        self.assertTrue(center.is_center)
        self.assertTrue(center.center_identifier)
        vals["center_id"] = center.id
        self.assertEqual(center.location_count, 0)
        location = self.env["res.partner"].create(vals)
        self.assertTrue(location.is_location)
        self.assertEqual(center.location_count, 1)
