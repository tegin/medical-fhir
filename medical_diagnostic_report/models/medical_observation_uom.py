# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class UomCategory(models.Model):
    _inherit = "uom.category"
    measure_type = fields.Char(required=True)


class UomUom(models.Model):
    _inherit = "uom.uom"

    measure_type = fields.Char(
        string="Type of measurement category",
        related="category_id.measure_type",
        store=True,
        readonly=True,
    )
    reference_format = fields.Char(default="%.2f")
