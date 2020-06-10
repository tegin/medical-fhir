# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WorkflowActivityDefinitionSuccessor(models.Model):

    _name = "workflow.activity.definition.successor"
    _description = "Activity Definition Successor"

    activity_definition_id = fields.Many2one(
        "workflow.activity.definition",
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    successor_id = fields.Many2one(
        "workflow.activity.definition", required=True, ondelete="cascade",
    )

    def _check_successor(self, request):
        return True
