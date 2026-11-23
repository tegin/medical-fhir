# Copyright 2022 Creu Blanca

from datetime import datetime

import freezegun

from odoo.exceptions import AccessError, UserError
from odoo.tests.common import TransactionCase


class TestClinicalImpression(TransactionCase):
    def setUp(self):
        super(TestClinicalImpression, self).setUp()
        self.patient = self.env["medical.patient"].create({"name": "Patient"})
        self.finding_pregnant = self.env["medical.clinical.finding"].create(
            {
                "name": "Pregnant",
                "create_condition_from_clinical_impression": True,
            }
        )
        self.finding_eye_infection = self.env["medical.clinical.finding"].create(
            {
                "name": "Eye infection",
                "create_condition_from_clinical_impression": False,
            }
        )
        self.allergy_substance_pollen = self.env["medical.allergy.substance"].create(
            {
                "name": "Pollen",
                "description": "Pollen",
            }
        )
        self.allergy_substance_ibuprofen = self.env["medical.allergy.substance"].create(
            {
                "name": "Ibuprofen",
                "description": "Ibuprofen",
                "create_warning": True,
            }
        )
        self.specialty_cardiology = self.env["medical.specialty"].create(
            {"name": "Cardiology", "description": "Cardiology"}
        )
        self.specialty_gynecology = self.env["medical.specialty"].create(
            {"name": "Gynecology", "description": "Gynecology"}
        )

    def test_validate_impression_fields(self):
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        with freezegun.freeze_time("2022-01-01 00:00:00"):
            impression.validate_clinical_impression()
        self.assertEqual(impression.validation_date, datetime(2022, 1, 1, 0, 0, 0))
        self.assertEqual(impression.validation_user_id.id, self.env.user.id)
        self.assertEqual(impression.fhir_state, "completed")

    def test_create_condition_from_impression_finding(self):
        self.assertEqual(self.patient.medical_condition_count, 0)
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_gynecology.id,
                "finding_ids": [
                    (4, self.finding_pregnant.id),
                    (4, self.finding_eye_infection.id),
                ],
            }
        )
        # It should create a condition for pregnant finding only
        impression.validate_clinical_impression()
        self.assertEqual(self.patient.medical_condition_count, 1)
        self.assertEqual(
            self.patient.medical_condition_ids[0].clinical_finding_id.id,
            self.finding_pregnant.id,
        )
        # If a new impression is created with the same finding,
        # it should not create a condition
        impression_2 = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_gynecology.id,
                "finding_ids": [(4, self.finding_pregnant.id)],
            }
        )
        impression_2.validate_clinical_impression()
        self.assertEqual(self.patient.medical_condition_count, 1)
        self.assertEqual(
            self.patient.medical_condition_ids[0].clinical_finding_id.id,
            self.finding_pregnant.id,
        )

    def test_create_allergy_from_impression_allergy_substance(self):
        self.assertEqual(self.patient.medical_allergies_count, 0)
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_gynecology.id,
                "allergy_substance_ids": [(4, self.allergy_substance_ibuprofen.id)],
            }
        )
        impression.validate_clinical_impression()
        self.assertEqual(self.patient.medical_allergies_count, 1)
        self.assertEqual(
            self.patient.medical_allergy_ids[0].allergy_id.id,
            self.allergy_substance_ibuprofen.id,
        )
        # If a new impression is created with the same allergy substance,
        # it should not create an allergy
        impression_2 = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_gynecology.id,
                "allergy_substance_ids": [(4, self.allergy_substance_ibuprofen.id)],
            }
        )
        impression_2.validate_clinical_impression()
        self.assertEqual(self.patient.medical_allergies_count, 1)
        self.assertEqual(
            self.patient.medical_allergy_ids[0].allergy_id.id,
            self.allergy_substance_ibuprofen.id,
        )

    def test_create_clinical_impression_report_action(self):
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_cardiology.id,
                "summary": "Summary 1",
            }
        )
        action = impression.action_create_clinical_impression_report()
        self.assertEqual(
            action["res_model"], "medical.patient.create.diagnostic.report"
        )
        self.assertEqual(action["context"]["default_patient_id"], self.patient.id)
        self.assertEqual(action["context"]["clinical_impression_ids"], [impression.id])

    def test_create_clinical_impressions_report_action_requires_selection(self):
        with self.assertRaises(UserError):
            self.env[
                "medical.clinical.impression"
            ].action_create_clinical_impressions_report()

    def test_create_clinical_impressions_report_action_same_patient_required(self):
        other_patient = self.env["medical.patient"].create({"name": "Other Patient"})
        impression_1 = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        impression_2 = self.env["medical.clinical.impression"].create(
            {
                "patient_id": other_patient.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        with self.assertRaises(UserError):
            (impression_1 | impression_2).action_create_clinical_impressions_report()

    def test_generate_without_template_outside_clinical_impression_is_blocked(self):
        wizard = self.env["medical.patient.create.diagnostic.report"].create(
            {"patient_id": self.patient.id}
        )
        with self.assertRaises(UserError):
            wizard.generate()

    def test_create_clinical_impression_report_appends_summary(self):
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_cardiology.id,
                "description": "Description 1",
                "summary": "Summary 1",
            }
        )
        impression.validate_clinical_impression()
        template = self.env["medical.diagnostic.report.template"].create(
            {"name": "Template 1", "composition": "Template composition"}
        )
        action = impression.action_create_clinical_impression_report()
        wizard = (
            self.env["medical.patient.create.diagnostic.report"]
            .with_context(**action["context"])
            .create({"template_id": template.id})
        )
        report_action = wizard.generate()
        report = self.env[report_action["res_model"]].browse(report_action["res_id"])
        self.assertIn(template.composition, report.composition)
        self.assertIn(impression.description, report.composition)
        self.assertIn(impression.summary, report.composition)
        # Each appended block must be preceded by its field's label in bold.
        fields_info = impression.fields_get(["description", "summary"])
        self.assertIn(
            "<b>%s</b>" % fields_info["description"]["string"], report.composition
        )
        self.assertIn(
            "<b>%s</b>" % fields_info["summary"]["string"], report.composition
        )
        # with_composition must be forced, or the composition field (and so
        # the appended content) stays hidden on the report form.
        self.assertTrue(report.with_composition)

    def test_create_clinical_impression_report_without_template(self):
        # template_id is not required when opened from a clinical impression:
        # the report is created blank and filled only with its content.
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_cardiology.id,
                "summary": "Summary 1",
            }
        )
        action = impression.action_create_clinical_impression_report()
        plain_wizard = self.env["medical.patient.create.diagnostic.report"].create(
            {"patient_id": self.patient.id}
        )
        self.assertFalse(plain_wizard.is_from_clinical_impression)
        wizard = (
            self.env["medical.patient.create.diagnostic.report"]
            .with_context(**action["context"])
            .create({})
        )
        self.assertTrue(wizard.is_from_clinical_impression)
        report_action = wizard.generate()
        report = self.env[report_action["res_model"]].browse(report_action["res_id"])
        self.assertIn(impression.summary, report.composition)

    def test_create_clinical_impressions_report_multiple_selection(self):
        impression_1 = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_cardiology.id,
                "summary": "Summary 1",
            }
        )
        impression_2 = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_cardiology.id,
                "summary": "Summary 2",
            }
        )
        impressions = impression_1 | impression_2
        action = impressions.action_create_clinical_impressions_report()
        self.assertEqual(action["context"]["default_patient_id"], self.patient.id)
        self.assertEqual(
            set(action["context"]["clinical_impression_ids"]), set(impressions.ids)
        )
        wizard = (
            self.env["medical.patient.create.diagnostic.report"]
            .with_context(**action["context"])
            .create({})
        )
        report_action = wizard.generate()
        report = self.env[report_action["res_model"]].browse(report_action["res_id"])
        self.assertIn(impression_1.summary, report.composition)
        self.assertIn(impression_2.summary, report.composition)
        self.assertIn(impression_1.internal_identifier, report.composition)
        self.assertIn(impression_2.internal_identifier, report.composition)

    def test_cancel_impression(self):
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_gynecology.id,
                "allergy_substance_ids": [(4, self.allergy_substance_ibuprofen.id)],
            }
        )
        impression.validate_clinical_impression()
        self.assertEqual(self.patient.medical_allergies_count, 1)
        impression.cancel_clinical_impression()
        # The allergies and findings created in that impression should be cancelled too.
        self.patient.invalidate_recordset()
        self.assertEqual(self.patient.medical_allergies_count, 0)

    def _create_cancelled_impression(self):
        impression = self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.patient.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        impression.validate_clinical_impression()
        impression.cancel_clinical_impression()
        return impression

    def _grant_revalidate_group(self):
        group = self.env.ref(
            "medical_clinical_impression.group_clinical_impression_revalidate"
        )
        self.env.user.write({"groups_id": [(4, group.id)]})

    def test_write_guarded_field_cancelled_without_revalidate_group(self):
        impression = self._create_cancelled_impression()
        self.assertFalse(impression.can_revalidate)
        with self.assertRaises(AccessError):
            impression.write({"summary": "New summary"})

    def test_write_guarded_field_cancelled_with_revalidate_group(self):
        impression = self._create_cancelled_impression()
        self._grant_revalidate_group()
        impression.invalidate_recordset()
        self.assertTrue(impression.can_revalidate)
        impression.write({"summary": "New summary"})
        self.assertEqual(impression.summary, "New summary")

    def test_write_non_guarded_field_cancelled_without_revalidate_group(self):
        # finding_ids is not part of _revalidate_guarded_fields, so it can
        # still be written even on a cancelled impression.
        impression = self._create_cancelled_impression()
        impression.write({"finding_ids": [(4, self.finding_pregnant.id)]})
        self.assertIn(self.finding_pregnant, impression.finding_ids)

    def test_revalidate_cancelled_without_revalidate_group(self):
        impression = self._create_cancelled_impression()
        with self.assertRaises(AccessError):
            impression.validate_clinical_impression()

    def test_revalidate_cancelled_with_revalidate_group(self):
        impression = self._create_cancelled_impression()
        self._grant_revalidate_group()
        impression.invalidate_recordset()
        impression.validate_clinical_impression()
        self.assertEqual(impression.fhir_state, "completed")
