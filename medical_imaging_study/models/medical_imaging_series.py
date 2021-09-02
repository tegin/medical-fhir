# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalImagingSeries(models.Model):

    _name = "medical.imaging.series"
    _description = "Medical Imaging Series"
    _order = "series_number"

    imaging_study_id = fields.Many2one(comodel_name="medical.imaging.study")

    series_number = fields.Char(readonly=True)

    instance_uid = fields.Char(index=True, readonly=True)

    modality_id = fields.Many2one(
        comodel_name="medical.imaging.acquisition.modality", readonly=True
    )

    description = fields.Text(readonly=True)

    instances_count = fields.Integer(
        string="Number of instances", readonly=True
    )  # This is a char because it will be extracted from the DICOM

    series_date = fields.Datetime(
        string="Date", readonly=True
    )  # It will be obtained from medical_fhir
    # FHIR: started

    state = fields.Selection(related="imaging_study_id.state", store=True)

    patient_id = fields.Many2one(
        comodel_name="medical.patient",
        related="imaging_study_id.patient_id",
        store=True,
    )

    encounter_id = fields.Many2one(
        comodel_name="medical.encounter",
        related="imaging_study_id.encounter_id",
        store=True,
    )

    _sql_constraints = [
        (
            "instance_uid_uniq",
            "UNIQUE (instance_uid)",
            "Instance UID must be unique.",
        )
    ]

    def _save_qido_data(self, study, dic):
        return {
            "instance_uid": dic["instance_uid"],
            "imaging_study_id": study.id,
            "series_number": dic["series_number"],
            "modality_id": self.env["medical.imaging.acquisition.modality"]
            .search([("code", "=", dic["modality"])], limit=1)
            .id,
            "series_date": dic["series_date"],
            "instances_count": dic["instances_count"],
            "description": dic["description"],
        }

    def _save_qido_data_from_study(self, study, dic):
        result = self._save_qido_data(study, dic)
        series = self.search(
            [("instance_uid", "=", dic["instance_uid"])], limit=1
        )
        if series:
            return (1, series.id, result)
        return (0, 0, result)
