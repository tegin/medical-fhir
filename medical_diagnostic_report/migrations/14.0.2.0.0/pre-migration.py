# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from openupgradelib import openupgrade

_field_spec = [
    (
        "template_type",
        "medical.diagnostic.report.template",
        "medical_diagnostic_report_template",
        "selection",
        False,
        "medical_diagnostic_report",
        "general",
    )
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_fields(env, _field_spec)
