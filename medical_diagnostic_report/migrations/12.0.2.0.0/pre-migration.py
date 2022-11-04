# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    if not openupgrade.column_exists(cr, "medical_observation", "state"):
        openupgrade.add_fields(
            env,
            [
                (
                    "state",
                    "medical.observation",
                    "medical_observation",
                    "selection",
                    False,
                    "medical_diagnostic_report",
                )
            ],
        )
        openupgrade.add_fields(
            env,
            [
                (
                    "observation_date",
                    "medical.observation",
                    "medical_observation",
                    "datetime",
                    False,
                    "medical_diagnostic_report",
                )
            ],
        )
        openupgrade.add_fields(
            env,
            [
                (
                    "patient_id",
                    "medical.observation",
                    "medical_observation",
                    "many2one",
                    False,
                    "medical_diagnostic_report",
                )
            ],
        )
        openupgrade.logged_query(
            cr,
            """
        UPDATE medical_observation obs
            SET state = report.state,
                observation_date = encounter.create_date,
                patient_id = report.patient_id
            FROM medical_diagnostic_report report
            INNER JOIN medical_encounter encounter
            ON encounter.id = report.encounter_id
            WHERE obs.diagnostic_report_id = report.id""",
        )
