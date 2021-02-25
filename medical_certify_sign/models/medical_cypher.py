# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime

from odoo import fields, models
from odoo.tools.config import config

_logger = logging.getLogger(__name__)
try:
    from cryptography.fernet import Fernet
except ImportError as err:
    _logger.debug(err)


class MedicalCypher(models.Model):
    _name = "medical.cypher"
    _description = "Medical Cypher"

    name = fields.Char(required=True)
    cypher_type = fields.Selection([("fernet", "Fernet")], required=True)
    fernet_config_key = fields.Char()

    def _get_fernet_cypher(self):
        return Fernet(config.get(self.fernet_config_key))

    def _sign_value(self, record):
        """Must return the values that will be written on the record"""
        return getattr(self, "_sign_digest_%s" % self.cypher_type)(record)

    def _sign_digest_fernet(self, record):
        digest = record.digest_current
        cypher = self._get_fernet_cypher()
        data = cypher.encrypt(digest.encode())
        return {
            "digital_signature": data.decode("utf-8"),
            "digest": digest,
            "signature_date": datetime.fromtimestamp(
                cypher.extract_timestamp(data)
            ),
        }

    def _verify_signature(self, record):
        """Must return a boolean checking if the record signature is valid"""
        return getattr(self, "_verify_signature_%s" % self.cypher_type)(record)

    def _verify_signature_fernet(self, record):
        data = self._get_fernet_cypher().decrypt(
            record.digital_signature.encode()
        )
        time = datetime.fromtimestamp(
            self._get_fernet_cypher().extract_timestamp(
                record.digital_signature.encode()
            )
        )
        return (
            data == record.digest_current.encode()
            and time == record.signature_date
        )
