# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import config

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    # FHIR Entity: Location (https://www.hl7.org/fhir/location.html)
    _inherit = "res.partner"

    is_center = fields.Boolean(default=False)
    center_id = fields.Many2one(
        "res.partner", domain=[("is_center", "=", True)]
    )
    location_ids = fields.One2many("res.partner", inverse_name="center_id")
    location_count = fields.Integer(compute="_compute_location_count")

    @api.depends("location_ids")
    def _compute_location_count(self):
        for record in self:
            record.location_count = len(record.location_ids)

    @api.constrains("is_location", "center_id")
    def check_location_center(self):
        test_condition = not config["test_enable"] or self.env.context.get(
            "test_check_location_center"
        )
        if not test_condition:
            return
        for record in self:
            if record.is_location and not record.center_id:
                raise ValidationError(
                    _("Center must be fullfilled on locations")
                )

    @api.model
    def default_medical_fields(self):
        result = super(ResPartner, self).default_medical_fields()
        result.append("is_center")
        return result

    def _check_medical(self, mode="write"):
        super()._check_medical(mode=mode)
        if (
            self.is_center
            and mode != "read"
            and not self.env.user.has_group(
                "medical_base.group_medical_configurator"
            )
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
