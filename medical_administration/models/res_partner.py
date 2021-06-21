# Copyright 2017 Creu Blanca
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import base64
import threading

from odoo import api, fields, models


class Partner(models.Model):
    # FHIR Entity: Person (http://hl7.org/fhir/person.html)
    _inherit = "res.partner"

    is_medical = fields.Boolean(default=False)

    @api.model
    def _get_medical_identifiers(self):
        """
        It must return a list of triads of check field, identifier field and
        defintion function
        :return: list
        """
        return []

    @api.model
    def create(self, vals):
        vals_upd = vals.copy()
        for (
            _medical,
            check,
            identifier,
            definition,
        ) in self._get_medical_identifiers():
            if vals_upd.get(check) and not vals_upd.get(identifier):
                vals_upd[identifier] = definition(vals_upd)
        if not vals_upd.get("image_1920"):
            vals_upd["image_1920"] = self._get_partner_default_image(vals_upd)
        return super(Partner, self).create(vals_upd)

    @api.model
    def _get_partner_default_image(self, vals):
        if self._get_default_image_path(vals):
            return self._get_default_medical_image(vals)
        return False

    @api.model
    def _get_default_image_path(self, vals):
        return False

    @api.model
    def _get_default_medical_image(self, vals):
        if getattr(
            threading.currentThread(), "testing", False
        ) or self._context.get("install_mode"):
            return False
        image_path = self._get_default_image_path(vals)
        if not image_path:
            return False
        with open(image_path, "rb") as f:
            image = f.read()
        return base64.b64encode(image)
