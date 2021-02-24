# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import json
from hashlib import sha512 as hash_func

from odoo import api, fields, models


class CertifyBase(models.AbstractModel):
    _name = "certify.base"
    _description = "Certify Base"

    digest = fields.Char(
        "Digest", readonly=True, help="Original Document Digest", copy=False
    )
    digest_altered = fields.Boolean(compute="_compute_digest")
    signature_altered = fields.Boolean(compute="_compute_digest")
    serializer_current = fields.Text("Current Doc", compute="_compute_digest")
    digest_current = fields.Char("Current Hash", compute="_compute_digest")
    digital_signature = fields.Text(
        "Digital Signature", readonly=True, copy=False
    )
    signature_date = fields.Datetime(readonly=True, copy=False)
    signature_qr = fields.Binary(
        string="Signature detail", compute="_compute_signature_qr"
    )
    cypher_id = fields.Many2one(
        "medical.cypher",
        readonly=True,
        copy=False,
        required=True,
        default=lambda r: r._get_cypher().id,
    )

    @api.depends("digital_signature")
    def _compute_signature_qr(self):
        report = self.env["ir.actions.report"]
        for rec in self:
            rec.signature_qr = base64.b64encode(
                report.qr_generate(
                    rec.digital_signature.encode(), error_correction=3
                )
            )

    @api.depends()
    def _compute_digest(self):
        for rec in self:
            serializer, digest = rec._generate_digest_data()
            rec.serializer_current = serializer
            rec.digest_current = digest
            rec.digest_altered = rec.digest and rec.digest != digest
            altered = False
            if rec.digital_signature:
                altered = (
                    rec.digest_altered
                    or not rec.cypher_id._verify_signature(rec)
                )
            rec.signature_altered = altered

    def _generate_digest_data(self):
        serializer = json.dumps(self._generate_serializer(), sort_keys=True)
        return serializer, self._generate_hash(serializer)

    def _generate_serializer(self):
        return {
            "id": self.id,
        }

    def _generate_hash(self, serializer):
        return hash_func(serializer.encode()).hexdigest()

    def _get_cypher(self):
        return self.env.ref("medical_certify.fernet_certify")

    def _generate_signature(self):
        cypher = self.cypher_id or self._get_cypher()
        vals = cypher._sign_value(self)
        if not self.cypher_id:
            vals["cypher_id"] = self.cypher_id.id
        return vals

    def _sign_document(self):
        self.ensure_one()
        if self.signature_date or self.digest or self.digital_signature:
            return
        self.write(self._generate_signature())

    def show_signature(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        return {
            "type": "ir.actions.act_window",
            "name": self.display_name,
            "res_model": self._name,
            "res_id": self.id,
            "target": "new",
            "view_mode": "form",
            "context": ctx,
            "views": [
                (
                    self.env.ref("medical_certify.certify_base_form_view").id,
                    "form",
                )
            ],
        }
