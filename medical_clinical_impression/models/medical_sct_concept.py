# Copyright 2021 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalSCTConcept(models.Model):
    _inherit = "medical.sct.concept"

    is_clinical_situation = fields.Boolean(
        store=True, index=True, compute="_compute_is_clinical_situation"
    )
    is_clinical_special_concept = fields.Boolean(
        store=True, index=True, compute="_compute_is_clinical_special_concept"
    )

    @api.depends("parent_ids")
    def _compute_is_clinical_situation(self):
        for record in self:
            record.is_clinical_situation = record.check_property(
                "is_clinical_situation", ["243796009"]
            )

    @api.depends("parent_ids")
    def _compute_is_clinical_special_concept(self):
        for record in self:
            record.is_clinical_special_concept = record.check_property(
                "is_clinical_special_concept", ["370115009"]
            )
