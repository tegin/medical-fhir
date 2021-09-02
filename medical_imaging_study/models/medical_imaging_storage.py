# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalImagingStorage(models.Model):

    _name = "medical.imaging.storage"
    _description = "Medical Imaging Storage"

    name = fields.Char()

    endpoint_ids = fields.One2many(
        comodel_name="medical.imaging.endpoint", inverse_name="storage_id"
    )
