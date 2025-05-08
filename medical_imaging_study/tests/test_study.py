# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import MagicMock, patch

from odoo.tests.common import TransactionCase


class TestStudy(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestStudy, cls).setUpClass()
        cls.storage = cls.env["medical.imaging.storage"].create(
            {
                "name": "Test Storage",
            }
        )
        cls.endpoint = cls.env["medical.imaging.endpoint"].create(
            {
                "name": "Test Endpoint",
                "storage_id": cls.storage.id,
                "connection_type": "dicom-qido-rs",
                "url": "http://example.com/dicomweb",
            }
        )

    @patch(
        "odoo.addons.medical_imaging_study.models.medical_imaging_endpoint.DICOMwebClient"
    )
    def test_1(self, MockDICOMwebClient):
        mock_client_instance = MagicMock()
        MockDICOMwebClient.return_value = mock_client_instance

        # Setup the return values for the mocked methods
        mock_client_instance.search_for_studies.return_value = [
            {
                "00080020": {"Value": ["20230101"]},
                "00080030": {"Value": ["000000"]},
                "00081030": {"Value": ["Test Study"]},
                "0020000D": {"Value": ["1.2.3"]},
                "00080050": {"Value": ["Test Accession Number"]},
            }
        ]
        mock_client_instance.search_for_series.return_value = [
            {
                "00080021": {"Value": ["20230101"]},
                "00080031": {"Value": ["000000"]},
                "0020000E": {"Value": ["4.5.6"]},
                "00200011": {"Value": ["1"]},
                "00080060": {"Value": ["MR"]},
                "00201209": {"Value": ["12"]},
                "0008103E": {"Value": ["Test Series"]},
            }
        ]

        self.env["medical.imaging.import.data"].create(
            {
                "study_uid": "1.2.3",
                "storage_id": self.storage.id,
            }
        ).import_imaging_study()
        study = self.env["medical.imaging.study"].search(
            [("instance_uid", "=", "1.2.3")]
        )
        self.assertTrue(
            study,
            "Study should be created",
        )
        self.assertTrue(study.series_ids)
        self.assertEqual(
            len(study.series_ids),
            1,
            "One series should be created",
        )
        self.assertEqual(
            study.series_ids[0].instance_uid,
            "4.5.6",
            "Series instance UID should be set correctly",
        )
        self.assertEqual(study.series_ids[0].instances_count, 12)
