# Copyright 2017 LasLabs Inc.
# Copyright 2017 CreuBlanca
# Copyright 2017 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class MedicalRole(models.Model):
    # FHIR Entity: PractitionerRole/code
    # (https://www.hl7.org/fhir/practitionerrole.html)
    _name = "medical.role"
    _description = "Practitioner Roles"

    name = fields.Char(required=True)
    description = fields.Char(required=True)
    active = fields.Boolean(default=True)
