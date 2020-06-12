# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalRequest(models.AbstractModel):

    _inherit = "medical.request"

    medical_careplan_id = fields.Many2one(
        string="Parent Medical Careplan",
        comodel_name="medical.careplan.medical",
        ondelete="restrict",
        index=True,
    )  # FHIR Field: BasedOn
    medical_careplan_ids = fields.One2many(
        string="Associated Medical CarePlans",
        comodel_name="medical.careplan.medical",
        compute="_compute_medical_careplan_ids",
    )
    medical_careplan_count = fields.Integer(
        compute="_compute_medical_careplan_ids",
        string="# of Medical Care Plans",
        copy=False,
        default=0,
    )

    show_medical_careplan = fields.Boolean(
        compute="_compute_show_medical_careplan"
    )

    def _compute_show_medical_careplan(self):
        for record in self:
            record.show_medical_careplan = record._name in [
                "medical.careplan.medical"
            ]

    @api.multi
    def _compute_medical_careplan_ids(self):
        inverse_field_name = self._get_parent_field_name()
        for rec in self:
            medical_careplans = self.env["medical.careplan.medical"].search(
                [(inverse_field_name, "=", rec.id)]
            )
            rec.medical_careplan_ids = [(6, 0, medical_careplans.ids)]
            rec.medical_careplan_count = len(rec.medical_careplan_ids)

    @api.model
    def _get_request_models(self):
        res = super(MedicalRequest, self)._get_request_models()
        res.append("medical.careplan.medical")
        return res

    @api.constrains("medical_careplan_id")
    def _check_hierarchy_medical_careplan(self):
        for record in self:
            record._check_hierarchy_children({})

    def _get_parents(self):
        res = super()._get_parents()
        res.append(self.medical_careplan_id)
        return res
