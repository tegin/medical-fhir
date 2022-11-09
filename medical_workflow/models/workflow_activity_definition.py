# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ActivityDefinition(models.Model):
    # FHIR entity: Activity Definition
    # (https://www.hl7.org/fhir/activitydefinition.html)
    _name = "workflow.activity.definition"
    _description = "Activity Definition"
    _order = "name"
    _parent_order = "name"
    _inherit = ["mail.thread", "mail.activity.mixin", "medical.abstract"]

    name = fields.Char(
        string="Name",
        help="Human-friendly name for the Plan Definition",
        required=True,
    )  # FHIR field: name
    description = fields.Text(
        string="Description", help="Summary of nature of plan"
    )  # FHIR field: description
    model_id = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
        domain=lambda self: [("model", "in", self._get_medical_models())],
    )  # FHIR field: kind
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("retired", "Retired"),
            ("unknown", "Unknown"),
        ],
        required=True,
        readonly=True,
        default="draft",
    )  # FHIR field: status
    service_id = fields.Many2one(
        string="Resource Product",
        comodel_name="product.product",
        help="Product that represents this resource",
        required=False,
        ondelete="restrict",
        index=True,
    )  # FHIR field: code
    quantity = fields.Integer(
        string="Quantity", help="How much to realize", default=1
    )  # FHIR field: quantity
    action_ids = fields.One2many(
        string="Subsequent actions",
        comodel_name="workflow.plan.definition.action",
        inverse_name="activity_definition_id",
        readonly=True,
    )
    active = fields.Boolean(compute="_compute_active", store=True)

    def _get_medical_models(self):
        return []

    @api.depends("state")
    def _compute_active(self):
        for record in self:
            record.active = bool(record.state == "active")

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code(
                "workflow.activity.definition"
            )
            or "/"
        )

    def _get_medical_values(
        self, vals, parent=False, plan=False, action=False
    ):
        if not vals.get("patient_id", False):
            raise ValidationError(_("Patient is not defined"))
        values = {
            "service_id": self.service_id.id,
            "plan_definition_id": plan
            and plan.id
            or action
            and action.plan_definition_id.id
            or False,
            "plan_definition_action_id": action and action.id or False,
            "activity_definition_id": self.id,
        }
        return values

    def _get_activity_values(
        self, vals, parent=False, plan=False, action=False
    ):
        values = vals.copy()
        values.update(self._get_medical_values(vals, parent, plan, action))
        return values

    def generate_record(self, values):
        return self.env[self.model_id.model].create(values)

    def execute_activity(self, vals, parent=False, plan=False, action=False):
        self.ensure_one()
        values = self._get_activity_values(vals, parent, plan, action)
        res = self.env[self.model_id.model]
        for _i in range(0, self.quantity):
            res |= self.generate_record(values)
        return res

    def _activate_vals(self):
        return {"state": "active"}

    def activate(self):
        self.write(self._activate_vals())

    def _reactivate_vals(self):
        return {"state": "active"}

    def reactivate(self):
        self.write(self._reactivate_vals())

    def _retire_vals(self):
        return {"state": "retired"}

    def retire(self):
        self.write(self._retire_vals())

    def action_show_plans(self):
        self.ensure_one()
        action = self.env.ref(
            "medical_workflow.workflow_plan_definition"
        ).read()[0]
        action["domain"] = [
            ("id", "in", self.action_ids.mapped("plan_definition_id").ids)
        ]
        return action
