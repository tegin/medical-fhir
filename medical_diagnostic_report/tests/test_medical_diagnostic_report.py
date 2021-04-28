# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import base64
from datetime import date, datetime

import freezegun
from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase
from odoo.tests.common import Form


class TestMedicalDiagnosticReport(TransactionCase):
    def setUp(self):
        super(TestMedicalDiagnosticReport, self).setUp()
        self.env.user.digital_signature = base64.b64encode(b"12345")
        self.patient_1 = self.env["medical.patient"].create(
            {"name": "Patient 1", "vat": "47238567H"}
        )
        self.encounter_1 = self.env["medical.encounter"].create(
            {"name": "Encounter 1", "patient_id": self.patient_1.id}
        )
        uom = self.env.ref(
            "medical_diagnostic_report.uom_ten_thousand_micro_liter"
        )
        self.concept_1 = self.env["medical.observation.concept"].create(
            {
                "name": "Concept 1",
                "value_type": "float",
                "uom_id": uom.id,
                "reference_range_low": 2,
                "reference_range_high": 10,
            }
        )
        items = [
            {"name": "Section 1", "display_type": "line_section"},
            {"name": "Subsection 1", "display_type": "line_subsection"},
            {
                "name": "Line 1",
                "reference_range_low": 2,
                "reference_range_high": 10,
                "uom_id": uom.id,
                "value_type": "float",
            },
            {
                "name": "Line 2",
                "reference_range_low": 2,
                "reference_range_high": 10,
                "uom_id": uom.id,
                "value_type": "int",
            },
            {"name": "Line 3", "value_type": "bool"},
            {"name": "Line 4", "value_type": "str"},
            {"name": "Note 1", "display_type": "line_note"},
            {"name": "Line 5", "concept_id": self.concept_1.id},
        ]
        self.template_1 = self.env[
            "medical.diagnostic.report.template"
        ].create(
            {
                "name": "Template 1",
                "with_observation": True,
                "with_conclusion": True,
                "conclusion": "Everything is ok",
                "with_composition": False,
                "item_ids": [(0, 0, item) for item in items],
            }
        )
        self.template_2 = self.env[
            "medical.diagnostic.report.template"
        ].create(
            {
                "name": "Template 2",
                "with_observation": True,
                "with_conclusion": False,
                "with_composition": True,
                "composition": "Composition 2",
                "item_ids": [(0, 0, item) for item in items],
            }
        )
        self.template_3 = self.env[
            "medical.diagnostic.report.template"
        ].create(
            {
                "name": "Template 3",
                "with_conclusion": True,
                "conclusion": "All the observations are in the reference range",
                "with_composition": True,
                "composition": "Composition 2",
            }
        )
        report_generation = self.env[
            "medical.encounter.create.diagnostic.report"
        ].create(
            {
                "encounter_id": self.encounter_1.id,
                "template_id": self.template_1.id,
            }
        )
        action = report_generation.generate()
        self.report = self.env[action.get("res_model")].browse(
            action.get("res_id")
        )

    def test_finalization(self):
        self.assertNotEqual(self.report.state, "final")
        self.assertFalse(self.report.issued_date)
        self.assertFalse(self.report.issued_user_id)
        self.assertTrue(self.report.is_editable)
        self.assertTrue(self.report.is_cancellable)
        with freezegun.freeze_time("2020-01-01"):
            self.report.registered2final_action()
        self.assertEqual(self.report.state, "final")
        self.assertTrue(self.report.issued_date)
        self.assertFalse(self.report.is_editable)
        self.assertTrue(self.report.is_cancellable)
        self.assertEqual(
            self.report.issued_date, datetime(2020, 1, 1, 0, 0, 0)
        )
        self.assertTrue(self.report.issued_user_id)
        self.assertEqual(self.report.issued_user_id, self.env.user)

        self.assertTrue(self.report.issued_user_id.digital_signature)
        self.assertEqual(
            self.report.issued_user_id.digital_signature,
            self.env.user.digital_signature,
        )

    def test_cancellation(self):
        self.assertNotEqual(self.report.state, "cancelled")
        self.assertFalse(self.report.cancel_date)
        self.assertFalse(self.report.cancel_user_id)
        self.assertTrue(self.report.is_editable)
        self.assertTrue(self.report.is_cancellable)
        with freezegun.freeze_time("2020-01-01"):
            self.report.cancel_action()
        self.assertEqual(self.report.state, "cancelled")
        self.assertTrue(self.report.cancel_date)
        self.assertEqual(
            self.report.cancel_date, datetime(2020, 1, 1, 0, 0, 0)
        )
        self.assertFalse(self.report.is_editable)
        self.assertFalse(self.report.is_cancellable)
        self.assertTrue(self.report.cancel_user_id)
        self.assertEqual(self.report.cancel_user_id, self.env.user)

    def test_age(self):
        self.patient_1.write({"birth_date": date(2002, 1, 1)})
        with freezegun.freeze_time("2020-01-01"):
            self.assertEqual(
                18,
                self.env["medical.diagnostic.report.template"]._compute_age(
                    self.patient_1
                ),
            )
        with freezegun.freeze_time("2019-12-31"):
            self.assertEqual(
                17,
                self.env["medical.diagnostic.report.template"]._compute_age(
                    self.patient_1
                ),
            )

    def test_report_generation(self):
        report_generation = self.env[
            "medical.encounter.create.diagnostic.report"
        ].create(
            {
                "encounter_id": self.encounter_1.id,
                "template_id": self.template_1.id,
            }
        )
        self.assertEqual(self.encounter_1.report_count, 1)
        action = report_generation.generate()
        report = self.env[action.get("res_model")].browse(action.get("res_id"))
        self.assertEqual(self.encounter_1.report_count, 2)
        self.assertEqual("medical.diagnostic.report", report._name)
        self.assertEqual(self.encounter_1, report.encounter_id)
        self.assertEqual(self.patient_1, report.patient_id)
        self.assertEqual(self.patient_1.name, report.patient_id.name)
        self.assertEqual(self.patient_1.vat, report.patient_id.vat)
        self.assertEqual(self.template_1.name, report.name)
        self.assertEqual(
            self.template_1.with_conclusion, report.with_conclusion
        )
        self.assertEqual(self.template_1.conclusion, report.conclusion)
        self.assertEqual(
            self.template_1.with_composition, report.with_composition
        )
        self.assertEqual(self.template_1.composition, report.composition)
        self.assertEqual(self.template_1.item_blocked, report.item_blocked)
        self.assertEqual(
            len(self.template_1.item_ids), len(report.observation_ids)
        )
        self.assertEqual(
            len(
                self.template_1.item_ids.filtered(lambda r: not r.display_type)
            ),
            len(report.observation_ids.filtered(lambda r: not r.display_type)),
        )
        self.assertEqual(
            len(
                self.template_1.item_ids.filtered(
                    lambda r: r.display_type == "line_section"
                )
            ),
            len(
                report.observation_ids.filtered(
                    lambda r: r.display_type == "line_section"
                )
            ),
        )
        self.assertEqual(
            len(
                self.template_1.item_ids.filtered(
                    lambda r: r.display_type == "line_subsection"
                )
            ),
            len(
                report.observation_ids.filtered(
                    lambda r: r.display_type == "line_subsection"
                )
            ),
        )
        self.assertEqual(
            len(
                self.template_1.item_ids.filtered(
                    lambda r: r.display_type == "line_note"
                )
            ),
            len(
                report.observation_ids.filtered(
                    lambda r: r.display_type == "line_note"
                )
            ),
        )

    def test_encounter_button(self):
        action = self.encounter_1.action_view_report()
        reports = self.env[action["res_model"]].search(action["domain"])
        self.assertIn(self.report, reports)

    def test_report_expand(self):
        self.assertFalse(self.report.composition)
        self.env["medical.diagnostic.report.expand"].create(
            {
                "diagnostic_report_id": self.report.id,
                "template_id": self.template_2.id,
            }
        ).merge()
        self.assertEqual(self.template_1.conclusion, self.report.conclusion)
        self.assertTrue(self.report.with_composition)
        self.assertTrue(self.report.composition)
        self.assertRegex(self.report.composition, self.template_2.composition)
        self.assertEqual(
            len(self.template_1.item_ids) + len(self.template_2.item_ids),
            len(self.report.observation_ids),
        )

    def test_report_expand_without_current_report_conclusion(self):
        report_generation = self.env[
            "medical.encounter.create.diagnostic.report"
        ].create(
            {
                "encounter_id": self.encounter_1.id,
                "template_id": self.template_2.id,
            }
        )
        action = report_generation.generate()
        report = self.env[action.get("res_model")].browse(action.get("res_id"))
        self.assertFalse(report.conclusion)
        self.env["medical.diagnostic.report.expand"].create(
            {
                "diagnostic_report_id": report.id,
                "template_id": self.template_3.id,
            }
        ).merge()
        self.assertTrue(report.with_conclusion)
        self.assertTrue(report.conclusion)
        self.assertRegex(report.conclusion, self.template_3.conclusion)

    def test_report_expand_same_template_exception(self):
        self.env["medical.diagnostic.report.expand"].create(
            {
                "diagnostic_report_id": self.report.id,
                "template_id": self.template_2.id,
            }
        ).merge()
        with self.assertRaises(ValidationError):
            self.env["medical.diagnostic.report.expand"].create(
                {
                    "diagnostic_report_id": self.report.id,
                    "template_id": self.template_2.id,
                }
            ).merge()

    def test_report_expand_same_template_no_exception(self):
        self.env["medical.diagnostic.report.expand"].create(
            {
                "diagnostic_report_id": self.report.id,
                "template_id": self.template_2.id,
            }
        ).merge()
        self.env["medical.diagnostic.report.expand"].create(
            {
                "diagnostic_report_id": self.report.id,
                "template_id": self.template_2.id,
            }
        ).with_context(no_raise_error_on_duplicate_template=True).merge()

    def test_report_expand_final_exception(self):
        self.assertEqual(self.report.state, "registered")
        self.report.registered2final_action()
        self.assertEqual(self.report.state, "final")
        with self.assertRaises(ValidationError):
            self.env["medical.diagnostic.report.expand"].create(
                {
                    "diagnostic_report_id": self.report.id,
                    "template_id": self.template_3.id,
                }
            ).merge()

    def test_report_form(self):
        with Form(self.template_3) as form:
            with form.item_ids.new() as observation:
                observation.concept_id = self.concept_1
                self.assertTrue(observation.name)
