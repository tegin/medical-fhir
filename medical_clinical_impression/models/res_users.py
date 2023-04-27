# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):

    _inherit = "res.users"
    specialty_ids = fields.Many2many("medical.specialty")
