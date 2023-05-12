# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalImagingStudy(models.Model):
    # FHIR Entity: ImagingStudy (https://www.hl7.org/fhir/imagingstudy.html)
    _name = "medical.imaging.study"
    _description = "Medical Imaging Study"

    name = fields.Char(
        compute="_compute_study_name", store=True
    )  # Not in FHIR

    instance_uid = fields.Char(index=True, readonly=True)

    state = fields.Selection(
        selection=[("registered", "Registered"), ("available", "Available")],
        default="available",
    )
    # FHIR: status

    modality_ids = fields.Many2many(
        comodel_name="medical.imaging.acquisition.modality",
        compute="_compute_modality_ids",
    )
    # FHIR: modality

    patient_id = fields.Many2one(comodel_name="medical.patient", readonly=True)
    # FHIR: subject

    encounter_id = fields.Many2one(
        comodel_name="medical.encounter", readonly=True
    )
    # FHIR: encounter

    study_date = fields.Datetime(string="Date", readonly=True)
    # FHIR: started

    series_count = fields.Integer(
        string="Number of Series",
        compute="_compute_series_count",
        readonly=True,
    )

    instances_count = fields.Integer(
        string="Number of Instances",
        compute="_compute_instances_count",
        readonly=True,
    )

    description = fields.Text(readonly=True)

    series_ids = fields.One2many(
        comodel_name="medical.imaging.series",
        inverse_name="imaging_study_id",
        copy=True,
        auto_join=True,
        readonly=True,
    )
    #  FHIR: series
    storage_ids = fields.Many2many(
        comodel_name="medical.imaging.storage", readonly=True
    )

    @api.depends("description")
    def _compute_study_name(self):
        for rec in self:
            if rec.description:
                rec.name = rec.description

    @api.depends("series_ids")
    def _compute_series_count(self):
        for rec in self:
            rec.series_count = len(rec.series_ids)

    @api.depends("series_ids")
    def _compute_instances_count(self):
        for rec in self:
            count = 0
            for series in rec.series_ids:
                count = count + series.instances_count
            rec.instances_count = count

    @api.depends("series_ids")
    def _compute_modality_ids(self):
        for rec in self:
            rec.modality_ids = None
            for series in rec.series_ids:
                rec.modality_ids = rec.modality_ids + series.modality_id

    _sql_constraints = [
        (
            "instance_uid_uniq",
            "UNIQUE (instance_uid)",
            "Instance UID must be unique.",
        )
    ]

    def _get_encounter_from_qido_data(self, dic):
        return [("name", "=", dic["accession_number"])]
        # TODO: cambiar name por internal_identifier

    def _save_qido_data(self, dic):
        result = {
            "study_date": dic["study_date"],
            "description": dic["description"],
            "series_ids": [
                self.env["medical.imaging.series"]._save_qido_data_from_study(
                    self, series
                )
                for series in dic["series_ids"]
            ],
        }
        encounter = self.env["medical.encounter"].search(
            self._get_encounter_from_qido_data(dic), limit=1
        )
        if encounter:
            result.update(
                {
                    "encounter_id": encounter.id,
                    "patient_id": encounter.patient_id.id,
                }
            )
        return result

    def update_study_data(self):
        self.ensure_one()
        self.storage_ids.mapped("endpoint_ids")._import_imaging_study(
            self.instance_uid
        )
