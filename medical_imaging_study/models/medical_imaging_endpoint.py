# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

import pytz
from dicomweb_client.api import DICOMwebClient
from dicomweb_client.session_utils import create_session_from_auth
from requests.auth import HTTPBasicAuth

from odoo import api, fields, models

from odoo.addons.base.models.res_partner import _tz_get


class MedicalImagingEndpoint(models.Model):

    _name = "medical.imaging.endpoint"
    _description = "Medical Imaging Endpoint"
    _inherit = ["server.env.techname.mixin", "server.env.mixin"]
    name = fields.Char()

    connection_type = fields.Selection(
        [("dicom-qido-rs", "Dicom Qido")],
        required=True,
        default="dicom-qido-rs",
    )
    url = fields.Char()
    user = fields.Char()
    password = fields.Char()
    storage_id = fields.Many2one(
        comodel_name="medical.imaging.storage", required=True
    )
    tz = fields.Selection(
        _tz_get,
        string="Timezone",
        default=lambda self: self.env.user.tz or "UTC",
    )

    def _add_study_fields_to_extract(self):
        return "00081030,00080201"

    def _add_series_fields_to_extract(self):
        return "00080021,00080031"

    def _import_imaging_study(self, study_uid):
        for endpoint in self:
            if endpoint.connection_type != "dicom-qido-rs":
                continue
            session = None
            if endpoint.user:
                auth = HTTPBasicAuth(endpoint.user, endpoint.password)
                session = create_session_from_auth(auth)
            client = DICOMwebClient(url=endpoint.url, session=session)

            data_study = client.search_for_studies(
                search_filters={"StudyInstanceUID": study_uid},
                fields=[self._add_study_fields_to_extract()],
            )
            if not data_study:
                continue
            data_series = client.search_for_series(
                study_uid, fields=[self._add_series_fields_to_extract()]
            )
            return endpoint._import_data_qido(data_study[0], data_series)

    def _import_data_qido(self, data_study, data_series):
        qido_data = self._process_study_qido_data(data_study, data_series)
        study = self.env["medical.imaging.study"].search(
            [("instance_uid", "=", qido_data["instance_uid"])]
        )
        result = study._save_qido_data(qido_data)
        result["storage_ids"] = [(4, self.storage_id.id)]
        if not study:
            result["instance_uid"] = qido_data["instance_uid"]
            study = study.create(result)
        else:
            study.update(result)
        return study.get_formview_action()

    def _process_study_qido_data(self, study_data, series_data):
        tz = self.tz or self.env.user.tz
        if "00080201" in study_data:
            tz = study_data["00080201"]["Value"][0]
        context_tz = pytz.timezone(tz)
        study_date = (
            context_tz.localize(
                datetime.strptime(
                    study_data["00080020"]["Value"][0]
                    + study_data["00080030"]["Value"][0],
                    "%Y%m%d%H:%M:%S",
                )
            )
            .astimezone(pytz.UTC)
            .replace(tzinfo=None)
        )
        return {
            "instance_uid": study_data["0020000D"]["Value"][0],
            "study_date": study_date,
            "accession_number": study_data["00080050"]["Value"][0],
            "description": study_data["00081030"]["Value"][0],
            "series_ids": self._process_series_qido_data(series_data),
        }

    def _process_series_qido_data(self, series_data):
        series_processed = []
        for series in series_data:
            context_tz = pytz.timezone(self.tz or self.env.user.tz)
            series_date = (
                context_tz.localize(
                    datetime.strptime(
                        series["00080021"]["Value"][0]
                        + series["00080031"]["Value"][0],
                        "%Y%m%d%H:%M:%S",
                    )
                )
                .astimezone(pytz.UTC)
                .replace(tzinfo=None)
            )
            dic = {
                "instance_uid": series["0020000E"]["Value"][0],
                "series_number": series["00200011"]["Value"][0],
                "modality": series["00080060"]["Value"][0],
                "description": series["0008103E"]["Value"][0],
                "instances_count": series["00201209"]["Value"][0],
                "series_date": series_date,
            }
            series_processed.append(dic)
        return series_processed

    @property
    def _server_env_fields(self):
        base_fields = super()._server_env_fields
        endpoint_fields = {
            "url": {},
            "user": {},
            "password": {},
        }
        endpoint_fields.update(base_fields)
        return endpoint_fields

    @api.model
    def _server_env_global_section_name(self):
        """Name of the global section in the configuration files

        Can be customized in your model
        """
        return "imaging_endpoint"
