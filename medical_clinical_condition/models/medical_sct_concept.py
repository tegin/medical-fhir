# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalSCTConcept(models.Model):
    _inherit = "medical.sct.concept"

    is_clinical_finding = fields.Boolean(
        store=True, index=True, compute="_compute_is_clinical_finding"
    )
    is_clinical_substance = fields.Boolean(
        store=True, index=True, compute="_compute_is_clinical_substance"
    )
    is_pharmaceutical_product = fields.Boolean(
        store=True, index=True, compute="_compute_is_pharmaceutical_product"
    )

    @api.depends("parent_ids")
    def _compute_is_clinical_finding(self):
        for record in self:
            record.is_clinical_finding = record.check_property(
                "is_clinical_finding", ["404684003"]
            )

    @api.depends("parent_ids")
    def _compute_is_clinical_substance(self):
        for record in self:
            record.is_clinical_substance = record.check_property(
                "is_clinical_substance", ["105590001"]
            )

    @api.depends("parent_ids")
    def _compute_is_pharmaceutical_product(self):
        for record in self:
            record.is_pharmaceutical_product = record.check_property(
                "is_pharmaceutical_product", ["373873005"]
            )
