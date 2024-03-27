# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalRequest(models.AbstractModel):
    # FHIR Entity: Request (https://www.hl7.org/fhir/request.html)
    _inherit = "medical.request"

    plan_definition_id = fields.Many2one(
        comodel_name="workflow.plan.definition",
        ondelete="restrict",
        index=True,
        readonly=True,
    )  # FHIR Field: definition
    activity_definition_id = fields.Many2one(
        comodel_name="workflow.activity.definition",
        ondelete="restrict",
        index=True,
        readonly=True,
    )  # FHIR Field: definition
    plan_definition_action_id = fields.Many2one(
        comodel_name="workflow.plan.definition.action",
        readonly=True,
    )  # FHIR Field: definition
