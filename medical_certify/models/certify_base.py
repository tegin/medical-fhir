# Copyright 2020 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import json
from hashlib import sha512 as hash_func

from odoo import api, fields, models


class DigestBase(models.AbstractModel):
    _name = "digest.base"
    _description = "Digest Base"
    _SIGNATURE_FIELD = "digest"

    digest = fields.Char(
        "Digest", readonly=True, help="Original Document Digest", copy=False
    )
    digest_altered = fields.Boolean(compute="_compute_digest")
    digest_current = fields.Char("Current Hash", compute="_compute_digest")
    serializer_current = fields.Text("Current Doc", compute="_compute_digest")
    signature_date = fields.Datetime(readonly=True, copy=False)
    signature_qr = fields.Binary(
        string="Signature detail", compute="_compute_signature_qr"
    )

    @api.depends(lambda r: [r._SIGNATURE_FIELD])
    def _compute_signature_qr(self):
        report = self.env["ir.actions.report"]
        for rec in self:
            if rec[rec._SIGNATURE_FIELD]:
                rec.signature_qr = base64.b64encode(
                    report.qr_generate(
                        rec[rec._SIGNATURE_FIELD].encode(),
                        error_correction=3,
                        back_color="white",
                        fill_color="black",
                    )
                )

    def _generate_digest_data(self):
        serializer = json.dumps(self._generate_serializer(), sort_keys=True)
        return serializer, self._generate_hash(serializer)

    def _generate_serializer(self):
        return {
            "id": self.id,
        }

    def _generate_hash(self, serializer):
        return hash_func(serializer.encode()).hexdigest()

    @api.depends()
    def _compute_digest(self):
        for rec in self:
            rec._compute_digest_one()

    def _compute_digest_one(self):
        serializer, digest = self._generate_digest_data()
        self.serializer_current = serializer
        self.digest_current = digest
        self.digest_altered = self.digest and self.digest != digest

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
                    self._show_signature_view().id,
                    "form",
                )
            ],
        }

    def _show_signature_view(self):
        return self.env.ref("medical_certify.certify_base_form_view")

    def _generate_signature(self):
        digest = self.digest_current
        return {"digest": digest, "signature_date": fields.Datetime.now()}

    def _sign_document(self):
        self.ensure_one()
        if self._check_signed():
            return
        self.write(self._generate_signature())

    def _check_signed(self):
        return self.signature_date or self.digest
