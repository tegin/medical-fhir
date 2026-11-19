# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalReport(models.Model):
    _name = "medical.report"
    _description = "Medical Report"
    _auto = False

    internal_identifier = fields.Char()
    patient_id = fields.Many2one("res.partner")
    date = fields.Datetime()
    is_draft = fields.Boolean()
    is_cancelled = fields.Boolean()
    user_id = fields.Many2one("res.users")
    model = fields.Char()
    description = fields.Text()

    def _queries(self):
        return []

    @property
    def _table_query(self):
        queries = self._queries()
        final_queries = []
        total_queries = len(queries)
        i = 0
        for query in queries:
            final_queries.append(query(i, total_queries))
            i += 1
        return " JOIN ".join(final_queries)
