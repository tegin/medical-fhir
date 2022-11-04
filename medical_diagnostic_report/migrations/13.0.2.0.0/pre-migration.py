# Copyright 2022 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(
        env.cr, "medical_diagnostic_report", "database_composition"
    ):
        openupgrade.rename_columns(
            env.cr,
            {
                "medical_diagnostic_report": [
                    ("composition", "database_composition")
                ]
            },
        )
    if not openupgrade.column_exists(
        env.cr, "medical_diagnostic_report", "database_conclusion"
    ):
        openupgrade.rename_columns(
            env.cr,
            {
                "medical_diagnostic_report": [
                    ("conclusion", "database_conclusion")
                ]
            },
        )
