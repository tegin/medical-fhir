# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime, timedelta

from odoo.tests import TransactionCase


class TestMedicalPatientObservationButtons(TransactionCase):
    def setUp(self):
        super(TestMedicalPatientObservationButtons, self).setUp()
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
        self.concept_2 = self.env["medical.observation.concept"].create(
            {
                "name": "Concept 2",
                "value_type": "int",
                "uom_id": uom.id,
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
            {"name": "Line 6", "concept_id": self.concept_2.id},
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

    def test_report_observations_change_state(self):
        report_observation = self.report.observation_ids[8]
        self.assertEqual(self.report.state, report_observation.state)
        self.report.registered2final_action()
        self.assertEqual(self.report.state, report_observation.state)
        self.report.cancel_action()
        self.assertEqual(self.report.state, report_observation.state)

    def test_action_view_observations_with_concept(self):
        self.report.registered2final_action()
        action = self.patient_1.action_view_observations_with_concept()
        observations = self.env[action["res_model"]].search(action["domain"])
        report_observation = self.report.observation_ids[8]
        self.assertIn(report_observation, observations)

    def test_compute_value_representation(self):
        self.report.registered2final_action()
        action = self.patient_1.action_view_observations_with_concept()
        report_observation = self.report.observation_ids[8]
        observation_patient = (
            self.env[action["res_model"]]
            .search(action["domain"])
            .search([("id", "=", report_observation.id)])
        )
        self.assertEqual(
            observation_patient.value_representation,
            str(
                getattr(
                    observation_patient,
                    "value_%s" % observation_patient.value_type,
                )
            ),
        )

    def test_compute_bokeh_chart(self):
        concept_evolution = self.env["patient.concept.evolution"].create(
            {"concept_id": self.concept_1.id, "patient_id": self.patient_1.id}
        )
        self.assertTrue(concept_evolution.bokeh_chart)
        self.assertRegex(concept_evolution.bokeh_chart, ".*No data found.*")
        self.report.registered2final_action()
        concept_evolution.refresh()
        self.assertRegex(
            concept_evolution.bokeh_chart,
            '.*<script type="text/javascript">.*',
        )
        concept_evolution.date_low_limit = (
            datetime.now() + timedelta(days=2)
        ).date()
        self.assertRegex(concept_evolution.bokeh_chart, ".*No data found.*")
        concept_evolution.date_low_limit = (
            datetime.now() + timedelta(days=-2)
        ).date()
        self.assertRegex(
            concept_evolution.bokeh_chart,
            '.*<script type="text/javascript">.*',
        )
        concept_evolution.date_low_limit = False
        concept_evolution.date_high_limit = (
            datetime.now() + timedelta(days=2)
        ).date()
        self.assertRegex(
            concept_evolution.bokeh_chart,
            '.*<script type="text/javascript">.*',
        )
        concept_evolution.date_high_limit = (
            datetime.now() + timedelta(days=-2)
        ).date()
        self.assertRegex(concept_evolution.bokeh_chart, ".*No data found.*")

    def test_compute_bokeh_chart_only_reference_range_high(self):
        concept_evolution = self.env["patient.concept.evolution"].create(
            {"concept_id": self.concept_2.id, "patient_id": self.patient_1.id}
        )
        self.report.registered2final_action()
        concept_evolution.refresh()
        self.assertRegex(
            concept_evolution.bokeh_chart,
            '.*<script type="text/javascript">.*',
        )
