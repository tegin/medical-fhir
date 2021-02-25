import logging

from odoo.tests import SavepointCase
from odoo.tools.config import config
from odoo_test_helper import FakeModelLoader

_logger = logging.getLogger(__name__)

try:
    from cryptography.fernet import Fernet
except ImportError as err:  # pragma: no cover
    _logger.debug(err)


class TestCertifySign(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._setup_records()
        cls.old_medical_integration_key = config.get(
            "medical_integration_key", ""
        )
        cls.crypting_key = Fernet.generate_key()
        # The key is encoded to bytes in the module, because in real life
        # the key com from the config file and is not in a binary format.
        # So we decode here to avoid having a special behavior because of
        # the tests.
        config["medical_integration_key"] = cls.crypting_key.decode()

    @classmethod
    def tearDownClass(cls):
        config["medical_integration_key"] = cls.old_medical_integration_key
        cls.loader.restore_registry()
        super().tearDownClass()

    @classmethod
    def _setup_records(cls):
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .fake_models import MedicalSignCertify

        cls.loader.update_registry((MedicalSignCertify,))
        cls.record = cls.env["medical.certify.sign.demo"].create(
            {"name": "NAME"}
        )

    def test_view(self):
        action = self.record.show_signature()
        new_record = self.env[action["res_model"]].browse(action["res_id"])
        self.assertEqual(new_record, self.record)

    def test_certify_signature_altered(self):
        self.assertFalse(self.record.digital_signature)
        self.record._sign_document()
        self.record.name = "OTHER NAME"
        self.record.refresh()
        self.assertTrue(self.record.digest)
        self.assertTrue(self.record.digest_altered)
        self.assertTrue(self.record.signature_altered)
        self.assertNotEqual(self.record.digest_current, self.record.digest)
        self.record.digest = self.record.digest_current
        self.record.refresh()
        self.assertFalse(self.record.digest_altered)
        self.assertTrue(self.record.signature_altered)

    def test_certify(self):
        self.assertTrue(self.record)
        self.assertTrue(self.record.serializer_current)
        self.assertTrue(self.record.digest_current)
        self.assertFalse(self.record.digest)
        self.assertFalse(self.record.digital_signature)
        digest = self.record.digest_current
        self.record._sign_document()
        self.assertTrue(self.record.digest)
        self.assertFalse(self.record.digest_altered)
        self.assertTrue(self.record.digital_signature)
        self.assertEqual(self.record.digest, digest)
        self.assertEqual(self.record.digest_current, digest)
        self.record.name = "OTHER NAME"
        self.record.refresh()
        self.assertTrue(self.record.digest)
        self.assertTrue(self.record.digest_altered)
        self.assertTrue(self.record.signature_altered)
        self.assertNotEqual(self.record.digest_current, digest)
        # Element cannot be signed again
        self.record._sign_document()
        self.assertTrue(self.record.digest)
        self.assertTrue(self.record.digest_altered)
        self.assertTrue(self.record.signature_altered)
        self.assertNotEqual(self.record.digest_current, digest)
