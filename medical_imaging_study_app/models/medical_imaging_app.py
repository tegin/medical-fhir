# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalImagingApp(models.Model):
    _name = "medical.imaging.app"
    _inherit = "image.mixin"
    _description = "Medical Imaging App"
    _order = "sequence, id"

    name = fields.Char(required=True)
    domain = fields.Char()
    ignore_domain = fields.Char()
    url = fields.Char()
    sequence = fields.Integer(default=10)
    app_type = fields.Selection(
        [("url", "URL")],
    )

    def _do_app_action_url(self, study):
        self.ensure_one()
        url = self.url
        if url and study.instance_uid:
            url = url.replace("{study_uid}", study.instance_uid)
            return {
                "type": "ir.actions.act_url",
                "url": url,
                "target": "new",
            }
        return {}
