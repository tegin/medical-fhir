# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WorkflowActivityDefinition(models.Model):
    _inherit = "workflow.activity.definition"

    successor_ids = fields.One2many(
        "workflow.activity.definition.successor",
        inverse_name="activity_definition_id",
    )
