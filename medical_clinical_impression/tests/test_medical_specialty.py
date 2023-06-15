# Copyright 2022 Creu Blanca

from datetime import datetime

import freezegun

from odoo.tests.common import TransactionCase


class TestClinicalSpecialty(TransactionCase):
    def setUp(self):
        super(TestClinicalSpecialty, self).setUp()

        self.specialty_cardiology = self.env["medical.specialty"].create(
            {"name": "Cardiology", "description": "Cardiology"}
        )
        self.specialty_gynecology = self.env["medical.specialty"].create(
            {"name": "Gynecology", "description": "Gynecology"}
        )



        user_1 = self.env["res.users"].create(
            {
                "name": "Test user 1",
                "specialty_id": self.specialty_cardiology.id,
                "groups_id": [
                    (
                        4,
                        self.env.ref("medical_base.group_medical_doctor").id,
                    ),
                ],
            }
        )
        user_2 = self.env["res.users"].create(
            {
                "name": "Test user 2",
                "specialty_id": self.specialty_cardiology.id,
                "groups_id": [
                    (
                        4,
                        self.env.ref("medical_base.group_medical_doctor").id,
                    ),
                ],
            }
        )


        self.env["create.impression.from.specialty"].create(
                {
                    "specialty_id": self.specialty_cardiology.id,
                }
            ).generate()

        self.env["create.impression.from.specialty"].create(
                {
                    "specialty_id": self.specialty_gynecology.id,
                }
            ).generate()

        self.env["create.impression.from.specialty"].create(
                {
                    "specialty_id": self.specialty_gynecology.id,
                }
            ).generate()



        self.user_1.refresh()
        self.assertEqual(len(self.patient.medical_impression_ids.ids), 0)
        self.assertEqual(len(self.patient.impression_specialty_ids.ids), 0)
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.user_1.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.user_2.id,
                "specialty_id": self.specialty_cardiology.id,
            }
        )
        self.env["medical.clinical.impression"].create(
            {
                "patient_id": self.user_1.id,
                "specialty_id": self.specialty_gynecology.id,
            }
        )
        self.assertEqual(len(self.user_1.medical_impression_ids.ids), 3)
        self.assertEqual(len(self.user_1.impression_specialty_ids.ids), 2)


#medico con espexialidad
#informes con especialidad


    def test_security(self):
        user_2 = self.env["res.users"].create(
            {
                "name": "Test user",
                "login": "test_report_user_2",
                "groups_id": [
                    (
                        4,
                        self.env.ref("medical_base.group_medical_doctor").id,
                    ),
                ],
            }
        )
        department_2 = self.env["medical.department"].create(
            {
                "name": "Department 2",
                "diagnostic_report_header": "Report Header 2",
                "user_ids": [(4, user_2.id)],
            }
        )
        category_3 = self.env["medical.report.category"].create(
            {"name": "Category 3", "medical_department_id": department_2.id}
        )
