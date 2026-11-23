# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from psycopg2 import sql

from odoo import fields, models, tools


class MedicalReport(models.Model):
    _name = "medical.report"
    _description = "Medical Report"
    _auto = False
    _log_access = True

    internal_identifier = fields.Char()
    # All the contributing models (medical.diagnostic.report,
    # medical.procedure.external.request, medical.laboratory.report, ...)
    # store a medical.patient id in their own patient_id column.
    patient_id = fields.Many2one("medical.patient")
    date = fields.Datetime()
    is_draft = fields.Boolean()
    is_cancelled = fields.Boolean()
    res_id = fields.Integer()
    user_id = fields.Many2one("res.users")
    model = fields.Selection(selection=[])
    description = fields.Text()
    # Set to a SQL "true" literal in a contributing model's
    # _basic_query_*_fields() to show the download button for that model;
    # defaults to NULL/False otherwise.
    has_download_report = fields.Boolean()

    def _queries(self):
        return []

    def _add_basic_query(self, related_model):
        def basic_query(index, total):
            related_self = self.env[related_model]
            fields = {
                field.name: (
                    field.name if related_self._fields.get(field.name) else "NULL"
                )
                for field in self._fields.values()
                if field.store and field.name not in ["id", "res_id", "model"]
            }
            fields["id"] = f"id * {total} + {index}"
            fields["res_id"] = "id"
            fields["model"] = f"'{related_self._name}'"
            fields.update(getattr(self, f"_basic_query_{related_self._table}_fields")())
            return f"""
                SELECT {', '.join([f'{value} as {field}' for field, value in fields.items()])}
                FROM {related_self._table}
            """

        return basic_query

    def get_formview_action(self, access_uid=None):
        self.ensure_one()
        record = self.env[self.model].browse(self.res_id)
        return record.get_formview_action(access_uid=access_uid)

    def open_document(self):
        self.ensure_one()
        return self.env[self.model].browse(self.res_id).open_document()

    def action_download_report(self):
        self.ensure_one()
        return self.env[self.model].browse(self.res_id).download_report()

    def init(self):
        queries = self._queries()
        final_queries = []
        total_queries = len(queries)
        i = 0
        for query in queries:
            final_queries.append(query(i, total_queries))
            i += 1
        query = " UNION ".join(final_queries)
        if not query:
            return
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(
            sql.SQL("CREATE or REPLACE VIEW {} as ({})").format(
                sql.Identifier(self._table), sql.SQL(query)
            )
        )
