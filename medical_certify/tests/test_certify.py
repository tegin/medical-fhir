from urllib.parse import urlparse

from odoo.tests import SavepointCase
from odoo_test_helper import FakeModelLoader


class TestCertify(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_records()

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    @classmethod
    def _setup_records(cls):
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .fake_models import MedicalCertify

        cls.loader.update_registry((MedicalCertify,))
        cls.record = cls.env["medical.certify.demo"].create({"name": "NAME"})

    def test_qr(self):
        self.record._sign_document()
        parsed_qr = urlparse(self.record.signature_qr)
        self.assertTrue(parsed_qr.path)

    def test_view(self):
        action = self.record.show_signature()
        new_record = self.env[action["res_model"]].browse(action["res_id"])
        self.assertEqual(new_record, self.record)

    def test_certify(self):
        self.assertTrue(self.record)
        self.assertTrue(self.record.serializer_current)
        self.assertTrue(self.record.digest_current)
        self.assertFalse(self.record.digest)
        digest = self.record.digest_current
        self.record._sign_document()
        self.assertTrue(self.record.digest)
        self.assertFalse(self.record.digest_altered)
        self.assertEqual(self.record.digest, digest)
        self.assertEqual(self.record.digest_current, digest)
        self.record.name = "OTHER NAME"
        self.record.refresh()
        self.assertTrue(self.record.digest)
        self.assertTrue(self.record.digest_altered)
        self.assertNotEqual(self.record.digest_current, digest)
        # Element cannot be signed again
        self.record._sign_document()
        self.assertTrue(self.record.digest)
        self.assertTrue(self.record.digest_altered)
        self.assertNotEqual(self.record.digest_current, digest)
