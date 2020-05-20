# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalCareplanMedicalAddPlanDefinition(models.TransientModel):
    _name = "medical.careplan.medical.add.plan.definition"
    _inherit = "medical.add.plan.definition"

    def _domain_plan_definition(self):
        return [
            (
                "type_id",
                "=",
                self.env.ref("medical_workflow.medical_workflow").id,
            )
        ]

    patient_id = fields.Many2one(
        related="medical_careplan_id.patient_id", readonly=True
    )

    medical_careplan_id = fields.Many2one(
        comodel_name="medical.careplan.medical",
        string="Medical Careplan",
        required=True,
    )

    plan_definition_id = fields.Many2one(
        comodel_name="workflow.plan.definition",
        domain=_domain_plan_definition,
        required=True,
    )

    def _get_context(self):
        return {
            "origin_model": self.medical_careplan_id._name,
            "origin_id": self.medical_careplan_id.id,
        }

    def _get_values(self):
        values = super()._get_values()
        values["medical_careplan_id"] = self.medical_careplan_id.id
        return values
