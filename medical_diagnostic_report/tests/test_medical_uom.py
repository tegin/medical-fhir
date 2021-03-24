# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestMedicalUom(TransactionCase):
    def _check(self, origin, destiny, original_qty, expected_qty):
        base_uom = self.env.ref("medical_diagnostic_report.%s" % origin)
        compute_uom = self.env.ref("medical_diagnostic_report.%s" % destiny)
        self.assertAlmostEqual(
            base_uom._compute_quantity(original_qty, compute_uom),
            expected_qty,
            places=2,
        )

    def test_rate(self):
        self._check("uom_rate", "uom_percentage", 1, 100)
        self._check("uom_percentage", "uom_rate", 200, 2)

    def test_density(self):
        self._check("uom_gram_liter", "uom_gram_deciliter", 10, 1)
        self._check("uom_gram_deciliter", "uom_gram_liter", 2, 20)
        self._check("uom_gram_liter", "uom_milligram_deciliter", 1, 100)
        self._check("uom_milligram_deciliter", "uom_gram_liter", 100, 1)
        self._check("uom_gram_deciliter", "uom_milligram_deciliter", 1, 1000)
        self._check("uom_milligram_deciliter", "uom_gram_deciliter", 2000, 2)
        self._check("uom_gram_liter", "uom_milligram_liter", 1, 1000)
        self._check("uom_milligram_liter", "uom_gram_liter", 2000, 2)

    def test_concentration(self):
        self._check(
            "uom_million_micro_liter", "uom_ten_thousand_micro_liter", 1, 100
        )
        self._check(
            "uom_ten_thousand_micro_liter", "uom_million_micro_liter", 200, 2
        )
        self._check(
            "uom_million_micro_liter", "uom_thousand_micro_liter", 1, 1000
        )
        self._check(
            "uom_thousand_micro_liter", "uom_million_micro_liter", 2000, 2
        )
        self._check(
            "uom_million_micro_liter", "uom_hundred_micro_liter", 1, 10000
        )
        self._check(
            "uom_hundred_micro_liter", "uom_million_micro_liter", 20000, 2
        )
        self._check(
            "uom_ten_thousand_micro_liter", "uom_thousand_micro_liter", 1, 10
        )
        self._check(
            "uom_thousand_micro_liter", "uom_ten_thousand_micro_liter", 20, 2
        )
        self._check(
            "uom_ten_thousand_micro_liter", "uom_hundred_micro_liter", 1, 100
        )
        self._check(
            "uom_hundred_micro_liter", "uom_ten_thousand_micro_liter", 200, 2
        )
        self._check(
            "uom_thousand_micro_liter", "uom_hundred_micro_liter", 1, 10
        )
        self._check(
            "uom_hundred_micro_liter", "uom_thousand_micro_liter", 20, 2
        )

    def test_concentration_water(self):
        self._check("uom_litre_litre", "uom_millilitre_litre", 1, 1000)
        self._check("uom_millilitre_litre", "uom_litre_litre", 2000, 2)

    def test_concentration_molar(self):
        self._check("uom_mol_litre", "uom_millimol_litre", 1, 1000)
        self._check("uom_millimol_litre", "uom_mol_litre", 2000, 2)

    def test_mol(self):
        self._check("uom_mol", "uom_femto_mol", 0.001, 1000000000000)
        self._check("uom_femto_mol", "uom_mol", 2000000000000000, 2)
        self._check("uom_mol", "uom_atto_mol", 0.000001, 1000000000000)
        self._check("uom_atto_mol", "uom_mol", 2000000000000000000, 2)
        self._check("uom_femto_mol", "uom_atto_mol", 1, 1000)
        self._check("uom_atto_mol", "uom_femto_mol", 2000, 2)

    def test_time_month_year(self):
        self._check("uom_hour", "uom_day", 24, 1)
        self._check("uom_day", "uom_hour", 2, 48)
        self._check("uom_hour", "uom_week", 168, 1)
        self._check("uom_week", "uom_hour", 2, 336)
        self._check("uom_day", "uom_week", 7, 1)
        self._check("uom_week", "uom_day", 2, 14)

    def test_time_hour_day_week(self):
        self._check("uom_month", "uom_year", 12, 1)
        self._check("uom_year", "uom_month", 1, 12)

    def test_femto_litre(self):
        base_uom = self.env.ref("uom.product_uom_litre")
        compute_uom = self.env.ref("medical_diagnostic_report.uom_femto_litre")
        self.assertAlmostEqual(
            base_uom._compute_quantity(0.001, compute_uom),
            1000000000000,
            places=2,
        )
        base_uom = self.env.ref("medical_diagnostic_report.uom_femto_litre")
        compute_uom = self.env.ref("uom.product_uom_litre")
        self.assertAlmostEqual(
            base_uom._compute_quantity(2000000000000000, compute_uom),
            2,
            places=2,
        )

    def test_pico_gram(self):
        base_uom = self.env.ref("uom.product_uom_kgm")
        compute_uom = self.env.ref("medical_diagnostic_report.uom_pico_gram")
        self.assertAlmostEqual(
            base_uom._compute_quantity(0.001, compute_uom),
            1000000000000,
            places=2,
        )
        base_uom = self.env.ref("medical_diagnostic_report.uom_pico_gram")
        compute_uom = self.env.ref("uom.product_uom_kgm")
        self.assertAlmostEqual(
            base_uom._compute_quantity(2000000000000000, compute_uom),
            2,
            places=2,
        )
