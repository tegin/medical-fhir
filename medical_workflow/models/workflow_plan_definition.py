# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .base_result import combine_result


class PlanDefinition(models.Model):
    # FHIR Entity: Plan Definition
    # (https://www.hl7.org/fhir/plandefinition.html)
    _name = "workflow.plan.definition"
    _description = "Plan Definition"
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
    active = fields.Boolean(compute="_compute_active", store=True)
    direct_action_ids = fields.One2many(
        string="Parent actions",
        comodel_name="workflow.plan.definition.action",
        inverse_name="direct_plan_definition_id",
    )  # FHIR field: action
    activity_definition_id = fields.Many2one(
        string="Activity definition",
        comodel_name="workflow.activity.definition",
    )  # FHIR field: action (if a parent action is created)
    action_ids = fields.One2many(
        string="All actions",
        comodel_name="workflow.plan.definition.action",
        inverse_name="plan_definition_id",
        readonly=True,
        copy=False,
    )

    @api.depends("state")
    def _compute_active(self):
        for record in self:
            record.active = bool(record.state == "active")

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"]
            .sudo()
            .next_by_code("workflow.plan.definition")
            or "/"
        )

    def _check_plan_recursion(self, plan_ids):
        self.ensure_one()
        if self.id in plan_ids:
            raise UserError(
                _("Error! You are attempting to create a recursive definition")
            )
        plan_ids.append(self.id)
        for action in self.action_ids:
            if action.execute_plan_definition_id:
                action.execute_plan_definition_id._check_plan_recursion(
                    plan_ids
                )

    def execute_plan_definition(self, vals, parent=False):
        """It will return the parent or the main activity.
        The action result could be of different models.
        """
        result, childs = self._execute_plan_definition(vals, parent)
        return result

    def _execute_plan_definition(self, vals, parent=False):
        self.ensure_one()
        res = False
        result = {}
        if (
            self.env.user._has_group(
                "medical_workflow." "group_main_activity_plan_definition"
            )
            and self.activity_definition_id
        ):
            res = self.activity_definition_id.execute_activity(
                vals, parent, plan=self
            )
            result[res._name] = res.ids
        if not res:
            res = parent
        final_result = res
        for action in self.direct_action_ids:
            child_res, child_result = action.execute_action(vals, res)
            result = combine_result(result, child_result)
            if not final_result:
                final_result = True
        return final_result, result

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

    def copy_data(self, default=None):
        if default is None:
            default = {}
        if "direct_action_ids" not in default:
            default["direct_action_ids"] = [
                (0, 0, line.copy_data()[0]) for line in self.direct_action_ids
            ]
        return super().copy_data(default)
