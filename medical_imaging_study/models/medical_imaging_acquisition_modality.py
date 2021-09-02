# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalImagingAcquisitionModality(models.Model):

    _name = "medical.imaging.acquisition.modality"
    _description = "Medical Imaging Acquisition Modality"

    name = fields.Char()
    code = fields.Char()
