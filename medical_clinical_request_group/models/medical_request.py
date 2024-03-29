# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalRequest(models.AbstractModel):
    _inherit = "medical.request"

    request_group_id = fields.Many2one(
        string="Parent Request group",
        comodel_name="medical.request.group",
        ondelete="restrict",
        index=True,
        readonly=True,
    )  # FHIR Field: BasedOn

    request_group_ids = fields.One2many(
        string="Parent Request Group",
        comodel_name="medical.request.group",
        compute="_compute_request_group_ids",
    )
    request_group_count = fields.Integer(
        compute="_compute_request_group_ids",
        string="# of Request Groups",
    )

    def _compute_request_group_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            request_groups = self.env["medical.request.group"].search(
                [(inverse_field_name, "=", rec.id)]
            )
            rec.request_group_ids = [(6, 0, request_groups.ids)]
            rec.request_group_count = len(rec.request_group_ids)

    @api.model
    def _get_request_models(self):
        res = super(MedicalRequest, self)._get_request_models()
        res.append("medical.request.group")
        return res

    @api.constrains("request_group_id")
    def _check_hierarchy_request_group(self):
        for record in self:
            record._check_hierarchy_children({})

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.request_group_id)
        return res
