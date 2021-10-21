# Copyright 2021 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class MedicalClinicalInvestigation(models.Model):

    _name = "medical.clinical.investigation"
    _inherit = "medical.abstract"
    _description = "Examination/Signs/History/Symptoms codes"

    name = fields.Char(required=True)
    description = fields.Char()
    sct_code_id = fields.Many2one(
        comodel_name="medical.sct.concept",
        domain=[
            "|",
            ("is_clinical_situation", "=", True),
            ("is_clinical_special_concept", "=", True),
        ],
    )

    @api.model
    def _get_internal_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code(
                "medical.clinical.investigation"
            )
            or "/"
        )
