# Copyright 2017 CreuBlanca
# Copyright 2017-2022 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class Partner(models.Model):
    # FHIR Entity: Person (http://hl7.org/fhir/person.html)
    _inherit = "res.partner"

    is_medical = fields.Boolean(default=False)
    is_practitioner = fields.Boolean(default=False)
    patient_ids = fields.One2many("medical.patient", inverse_name="partner_id")
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
    def _get_medical_identifiers(self):
        """
        It must return a list of triads of check field, identifier field and
        defintion function
        :return: list
        """
        return []

    @api.model_create_multi
    def create(self, vals_list):
        partners = super(Partner, self).create(vals_list)
        for partner in partners:
            if partner.is_medical or partner.patient_ids:
                partner.check_medical("create")
        return partners

    def write(self, vals):
        result = super(Partner, self).write(vals)
        for partner in self:
            if partner.is_medical or partner.patient_ids:
                partner.check_medical("write")
        return result

    def unlink(self):
        for partner in self:
            if partner.is_medical or partner.sudo().patient_ids:
                partner.check_medical("unlink")
        return super(Partner, self).unlink()

    def check_medical(self, mode="write"):
        if self.env.su:
            return
        self._check_medical(mode=mode)

    def _check_medical(self, mode="write"):
        if self.sudo().patient_ids:
            self.sudo().patient_ids.check_access_rights(mode)
        if (
            self.is_medical
            and not self.env.user.has_group("medical_base.group_medical_user")
            and mode != "read"
        ):
            # DUPLICIDAD DE CÓDIGO
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
        # HASTA AQUÍ
        if (
            self.is_practitioner
            and mode != "read"
            and not self._check_medical_practitioner()
        ):
            # DUPLICIDAD DE CÓDIGO
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
        # HASTA AQUÍ

    @api.model
    def default_medical_fields(self):
        result = ["is_medical"]
        result.append("is_practitioner")
        return result

    @api.model
    def default_get(self, fields_list):
        """We want to avoid to pass the medical_fields on the childs of the partner"""
        result = super(Partner, self).default_get(fields_list)
        for field in self.default_medical_fields():
            if result.get(field) and self.env.context.get("default_parent_id"):
                result[field] = False
        return result

    def _check_medical_practitioner(self):
        return self.env.user.has_group("medical_base.group_medical_configurator")
