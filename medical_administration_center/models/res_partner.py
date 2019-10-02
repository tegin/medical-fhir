# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    # FHIR Entity: Location (https://www.hl7.org/fhir/location.html)
    _inherit = "res.partner"

    is_center = fields.Boolean(default=False)
    center_identifier = fields.Char(readonly=True)  # FHIR Field: identifier
    center_id = fields.Many2one(
        "res.partner", domain=[("is_center", "=", True)]
    )
    location_ids = fields.One2many("res.partner", inverse_name="center_id")
    location_count = fields.Integer(compute="_compute_location_count")

    @api.multi
    @api.depends("location_ids")
    def _compute_location_count(self):
        for record in self:
            record.location_count = len(record.location_ids)

    @api.constrains("is_location", "center_id")
    def check_location_center(self):
        if self.is_location and not self.center_id:
            raise ValidationError(_("Center must be fullfilled on locations"))

    @api.model
    def _get_medical_identifiers(self):
        res = super(ResPartner, self)._get_medical_identifiers()
        res.append(
            (
                "is_medical",
                "is_center",
                "center_identifier",
                self._get_center_identifier,
            )
        )
        return res

    @api.model
    def _get_center_identifier(self, vals):
        return self.env["ir.sequence"].next_by_code("medical.center") or "/"
