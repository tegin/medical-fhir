# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalAdministrationRoute(models.Model):

    _name = "medical.administration.route"
    _description = "Medical Administration Route"

    name = fields.Char()
