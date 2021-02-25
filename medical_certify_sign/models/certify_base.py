# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class CertifyBase(models.AbstractModel):
    _name = "certify.base"
    _inherit = "digest.base"
    _description = "Certify Base"
    _SIGNATURE_FIELD = "digital_signature"

    signature_altered = fields.Boolean(compute="_compute_digest")
    digital_signature = fields.Text(
        "Digital Signature", readonly=True, copy=False
    )
    cypher_id = fields.Many2one(
        "medical.cypher",
        readonly=True,
        copy=False,
        required=True,
        default=lambda r: r._get_cypher().id,
    )

    def _compute_digest_one(self):
        super(CertifyBase, self)._compute_digest_one()
        altered = False
        if self.digital_signature:
            altered = (
                self.digest_altered
                or not self.cypher_id._verify_signature(self)
            )
        self.signature_altered = altered

    def _get_cypher(self):
        return self.env.ref("medical_certify_sign.fernet_certify")

    def _show_signature_view(self):
        return self.env.ref("medical_certify_sign.certify_base_sign_form_view")

    def _check_signed(self):
        return super()._check_signed() or self.digital_signature

    def _generate_signature(self):
        vals = super(CertifyBase, self)._generate_signature()
        cypher = self.cypher_id or self._get_cypher()
        vals.update(cypher._sign_value(self))
        if not self.cypher_id:
            vals["cypher_id"] = self.cypher_id.id
        return vals
