# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalImagingImportData(models.TransientModel):

    _name = "medical.imaging.import.data"
    _description = "Medical Imaging Import Data"

    study_uid = fields.Char()

    storage_id = fields.Many2one(
        comodel_name="medical.imaging.storage", required=True
    )

    def import_imaging_study(self):
        if self.study_uid and self.storage_id:
            return self.storage_id.endpoint_ids._import_imaging_study(
                self.study_uid
            )
