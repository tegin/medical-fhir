# Copyright 2017 LasLabs Inc.
# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


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

    @api.model
    def default_medical_fields(self):
        result = super(ResPartner, self).default_medical_fields()
        result.append("is_practitioner")
        return result

    def _check_medical(self, mode="write"):
        result = super()._check_medical(mode=mode)
        if (
            self.is_practitioner
            and mode != "read"
            and not self._check_medical_practitioner()
        ):
            _logger.info(
                "Access Denied by ACLs for operation: %s, uid: %s, model: %s",
                "write",
                self._uid,
                self._name,
            )
            raise AccessError(
                _(
                    "You are not allowed to %(mode)s medical Contacts (res.partner) records.",
                    mode=mode,
                )
            )
        return result

    def _check_medical_practitioner(self):
        return self.env.user.has_group("medical_base.group_medical_configurator")
