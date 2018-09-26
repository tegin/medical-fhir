# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from .base_result import combine_result


class PlanDefinition(models.Model):
    # FHIR Entity: Plan Definition
    # (https://www.hl7.org/fhir/plandefinition.html)
    _name = 'workflow.plan.definition'
    _description = 'Plan Definition'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'medical.abstract']

    name = fields.Char(
        string='Name',
        help='Human-friendly name for the Plan Definition',
        required=True,
    )   # FHIR field: name
    description = fields.Text(
        string='Description',
        help='Summary of nature of plan',
    )   # FHIR field: description
    type_id = fields.Many2one(
        string='Workflow type',
        comodel_name='workflow.type',
        ondelete='restrict', index=True,
        required=True,
    )   # FHIR field: type
    state = fields.Selection(
        [('draft', 'Draft'),
         ('active', 'Active'),
         ('retired', 'Retired'),
         ('unknown', 'Unknown')],
        required=True,
        default='draft',
    )   # FHIR field: status
    direct_action_ids = fields.One2many(
        string='Parent actions',
        comodel_name='workflow.plan.definition.action',
        inverse_name='direct_plan_definition_id',
    )   # FHIR field: action
    activity_definition_id = fields.Many2one(
        string='Activity definition',
        comodel_name='workflow.activity.definition',
        description='Main action',
    )   # FHIR field: action (if a parent action is created)
    action_ids = fields.One2many(
        string='All actions',
        comodel_name='workflow.plan.definition.action',
        inverse_name='plan_definition_id',
        readonly=True,
    )

    @api.model
    def _get_internal_identifier(self, vals):
        return self.env['ir.sequence'].next_by_code(
            'workflow.plan.definition') or '/'

    @api.multi
    def _check_plan_recursion(self, plan_ids):
        self.ensure_one()
        if self.id in plan_ids:
            raise UserError(_(
                'Error! You are attempting to create a recursive definition'))
        plan_ids.append(self.id)
        for action in self.action_ids:
            if action.execute_plan_definition_id:
                action.execute_plan_definition_id._check_plan_recursion(
                    plan_ids
                )

    @api.multi
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
            self.env.user._has_group('medical_workflow.'
                                     'group_main_activity_plan_definition') and
            self.activity_definition_id
        ):
            res = self.activity_definition_id.execute_activity(
                vals, parent, plan=self)
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
