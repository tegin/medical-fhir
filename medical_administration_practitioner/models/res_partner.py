# Copyright 2017 LasLabs Inc.
# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models
from odoo.modules import get_module_resource


class ResPartner(models.Model):
    # FHIR Entity: Practitioner (https://www.hl7.org/fhir/practitioner.html)
    _inherit = "res.partner"

    is_practitioner = fields.Boolean(default=False)
    practitioner_role_ids = fields.Many2many(
        string="Practitioner Roles", comodel_name="medical.role"
    )  # FHIR Field: PractitionerRole/role
    practitioner_type = fields.Selection(
        string="Entity Type",
        selection=[
            ("internal", "Internal Entity"),
            ("external", "External Entity"),
        ],
        readonly=False,
    )
    practitioner_identifier = fields.Char(
        readonly=True
    )  # FHIR Field: identifier

    @api.model
    def _get_medical_identifiers(self):
        res = super(ResPartner, self)._get_medical_identifiers()
        res.append(
            (
                "is_medical",
                "is_practitioner",
                "practitioner_identifier",
                self._get_practitioner_identifier,
            )
        )
        return res

    @api.model
    def _get_practitioner_identifier(self, vals):
        return (
            self.env["ir.sequence"].next_by_code("medical.practitioner") or "/"
        )

    @api.model
    def _get_default_image_path(self, vals):
        if vals.get("is_practitioner", False):
            return get_module_resource(
                "medical_administration_practitioner",
                "static/src/img",
                "practitioner-avatar.png",
            )

    @api.model
    def default_medical_fields(self):
        result = super(ResPartner, self).default_medical_fields()
        result.append("is_practitioner")
        return result
