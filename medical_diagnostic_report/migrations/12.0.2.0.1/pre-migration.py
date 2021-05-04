# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(
        env.cr, "medical_diagnostic_report_template", "title"
    ):
        openupgrade.add_fields(
            env,
            [
                (
                    "title",
                    "medical.diagnostic.report.template",
                    "medical_diagnostic_report_template",
                    "char",
                    False,
                    "medical_diagnostic_report",
                )
            ],
        )
        model = "medical.diagnostic.report.template"
        old_field = "name"
        new_field = "title"
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE ir_translation
            SET name = %s
            WHERE name = %s
                AND type = 'model'
            """,
            (
                "{},{}".format(model, new_field),
                "{},{}".format(model, old_field),
            ),
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE medical_diagnostic_report_template
            SET title= name""",
        )
