# Copyright 2022 Creu Blanca
from mock import patch
from datetime import datetime
from odoo import models, api


class TestClinicalImpressionSecurity(MedicalSavePointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.patient = cls.env["medical.patient"].create({"name": "Patient"})
        cls.encounter = cls.env["medical.encounter"].create(
                {
                    "patient_id": cls.patient.id,
                    "create_date": fields.Datetime.now(),
                }
            )
        cls.specialty_cardiology = cls.env["medical.specialty"].create(
            {"name": "Cardiology", "description": "Cardiology",}
        )
        cls.specialty_gynecology = cls.env["medical.specialty"].create(
            {"name": "Gynecology", "description": "Gynecology",}
        )
        user_1 = cls.env["res.users"].create(
            {
                "name": "Test user 1",
                "specialty_id": cls.specialty_cardiology.id,
                "groups_id": [
                    (
                        4,
                        cls.env.ref("medical_base.group_medical_doctor").id,
                    ),
                ],
            }
        )

        user_2 = cls.env["res.users"].create(
            {
                "name": "Test user 2",
                "specialty_id": cls.specialty_gynecology.id,
                "groups_id": [
                    (
                        4,
                        cls.env.ref("medical_base.group_medical_doctor").id,
                    ),
                ],
            }
        )

        manager = cls.env["res.users"].create(
            {
                "name": "Test user 2",
                "specialty_id": cls.specialty_cardiology.id,
                "groups_id": [
                    (
                        4,
                        cls.env.ref("medical_base.group_medical_doctor_manager").id,
                    ),
                ],
            }
        )

        # TODO: Hacer funcion. ???? Primero que funcione
        impression_1 = cls.env["medical.clinical.impression"].with_user(cls.user_1).create(
            {
                "patient_id": cls.patient.id,
                "encounter_id": cls.encounter.id,
                "specialty_id": cls.specialty_cardiology.id,
            }
        )

        impression_2 = cls.env["medical.clinical.impression"].with_user(cls.user_2).create(
            {
                "patient_id": cls.patient.id,
                "encounter_id": cls.encounter.id,
                "specialty_id": cls.specialty_ginecology.id,
            }
        )
        impression_3 = cls.env["medical.clinical.impression"].with_user(cls.user_1).create(
            {
                "patient_id": cls.patient.id,
                "encounter_id": cls.encounter.id,
                "specialty_id": cls.specialty_ginecology.id,
            }
        )

    def test_security_unlink(self):
        """
        Error al borrar una impression, por no ser el usuario creador ni el manager de la especialidad.
        """
        with self.assertRaises(AccessError):
            self.impression_2.with_user(self.user_1).unlink()
        with self.assertRaises(AccessError):
            self.impression_1.with_user(self.user_2).unlink()
        with self.assertRaises(AccessError):
            self.impression_2.with_user(self.manager).unlink()

    #     def test_security_write(self):
    #     """
    #     Error al escribir en una impression, por no ser el usuario creador ni el manager de la especialidad.
    #     """
    #     with self.assertRaises(AccessError):
    #         self.impression_2.with_user(self.user_1).write()
    #     with self.assertRaises(AccessError):
    #         self.impression_1.with_user(self.user_2).write()
    #     with self.assertRaises(AccessError):
    #         self.impression_2.with_user(self.manager).write()

    #    def test_security_create(self): ##AQUI PONDRIAMOS LA DE CREATE, ES NECESARIA?
    #     """
    #     Error al crear en una impression, por no ser el usuario creador ni el manager de la especialidad.
    #     """
    #     with self.assertRaises(AccessError):
    #         self.impression_2.with_user(self.user_1).create()
    #     with self.assertRaises(AccessError):
    #         self.impression_1.with_user(self.user_2).create()
    #     with self.assertRaises(AccessError):
    #         self.impression_2.with_user(self.manager).create()




#            # AHORA MIRAR CUANDO NO HAY ERROR

#            # el usuario no creador puede leer ()
#            #

#     def test_security_read(self): ##AQUI PONDRIAMOS LA DE leer, ES NECESARIA?
#         """
#         NO Error ??? al crear en una impression, por no ser el usuario creador ni el manager de la especialidad.
#         """
#         with self.assertRaises(AccessError):
#             self.impression_2.with_user(self.user_1).create()
#         with self.assertRaises(AccessError):
#             self.impression_1.with_user(self.user_2).create()
#         with self.assertRaises(AccessError):
#             self.impression_2.with_user(self.manager).create()



#         self.assertEqual(len(self.patient.medical_impression_ids.ids), 0) # medico ha creado una impression de gine/cardio
#         #el med. puede leer, borrar la impresion que antes hemos comprovado que ha creado

#         # Se confima que hay un ERROR y el medico creador No puede crear borrar ni leer lo qu eNO es de su especialidad.

#         # El manager no creador de un impression puede hacelo todo de una impression

# ## El usuario creador puede leer, escribir, crear y borrar la impression que ha creado.(?)

# ## El usuario NO creador, NO puede escribir, crear y borrar la impression que NO ha creado. (X)

# ## El usuario NO creador puede leer la impression que NO ha creado. (?)



# ## El manager de una especialidad puede puede leer, escribir, crear y borrar la impression que SI es de su especialidad. (?)

# ## El manager de una especialidad NO puede escribir, crear y borrar en la impression que NO es de su especialidad. (X)

# ## El manager de una especialidad puede puede leer la impression que NO es de su especialidad. [Esta no falta, el manager es un usuari i si es complix l'última, no fa falta]





#         self.user_1.refresh()
#         # Si vamos a hacer verificaciones, es que probablemente esto debe ir dentro de un test,
#         # En este caso podriamos crear, las especialidades, Usuarios (cardiologo, gynecologo,
#         #        resp. area gynecologia), paciente y afiliación**
#         # Si vemos que una parte la estamos repitiendo constantemente, podemos añadirlo en una función e ir reutilizandola:
#         # En este caso, podríamos añadir una función que ons cree una especialidad usando el formulario y le pasamos como parámetro el usuario y la especialidad
#         self.assertEqual(len(self.patient.medical_impression_ids.ids), 0)
#         self.assertEqual(len(self.patient.impression_specialty_ids.ids), 0)
#         self.assertEqual(len(self.user_1.medical_impression_ids.ids), 3)
#         self.assertEqual(len(self.user_1.impression_specialty_ids.ids), 2)

#     # medico con espexialidad
#     # informes con especialidad

#     def create_impression_for_test(self, patient, encounter, user):
#         impression = self.env["medical.clinical.impression"].create(
#             {
#                 "patient_id": patient.id,
#                 "patient_id": patient.id,
#                 "encounter_id": encounter.id,
#                 "specialty_id": self.specialty_cardiology.id,
#             }
#         )


#     @api.model  # Necessitem l'usuari ja que a les regles vam fer el ('create_uid', '=', user.id)]
#     def generate_impressions(self, patient_id, encounter_id, specialty_ids):
#         impressions = self.env['medical.clinical.impression']

#         for specialty_id in specialty_ids:
#             impression = self.env['medical.clinical.impression'].create({
#                 'patient_id': patient_id,
#                 'encounter_id': encounter_id,
#                 'specialty_id': specialty_id,
#             })
#             impressions += impression

#         return impressions

#     def example_usage(self):
#         specialty_ids = [
#             self.specialty_cardiology.id,
#             self.specialty_ginecology.id,
#             self.specialty_ginecology.id,
#         ]
#         impressions = self.generate_impressions(self.patient.id, self.encounter.id, specialty_ids)
#         impression_1, impression_2, impression_3 = impressions[:3] #realment igual no fa falta
