# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MedicalAbstract(models.AbstractModel):
    # FHIR Entity: default entity, as all models have internal_identifiers
    _name = "medical.abstract"
    _description = "Default FHIR entity"

    internal_identifier = fields.Char(
        name="Identifier",
        help="Internal identifier used to identify this record",
        readonly=True,
        default="/",
        copy=False,
    )  # FHIR Field: identifier

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("internal_identifier", "/") == "/":
                vals["internal_identifier"] = self._get_internal_identifier(vals)
        return super().create(vals_list)

    def _get_internal_identifier(self, vals):
        # It should be rewritten for each element
        raise UserError(_("Function is not defined"))
