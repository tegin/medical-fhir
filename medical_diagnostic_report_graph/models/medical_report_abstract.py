# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalReportAbstract(models.AbstractModel):

    _inherit = "medical.report.abstract"

    compute_graph = fields.Boolean()

    hide_observations = fields.Boolean(help="Hide observations on report")
