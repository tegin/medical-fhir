# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests import TransactionCase


class TestMedication(TransactionCase):
    def setUp(self):
        super(TestMedication, self).setUp()
        self.atc_code = self.env["medical.atc.concept"].search(
            [("parent_id", "!=", False)], limit=1
        )

    def test_atc_code(self):
        code = self.atc_code.code
        self.atc_code.level_code = self.atc_code.level_code + "B"
        self.assertEqual(self.atc_code.code, code + "B")
