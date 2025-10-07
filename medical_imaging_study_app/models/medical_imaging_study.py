# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class MedicalImagingStudy(models.Model):

    _inherit = "medical.imaging.study"

    app_info = fields.Json(compute="_compute_app_info")

    @api.depends("storage_ids")
    def _compute_app_info(self):
        for study in self:
            apps = self.env["medical.imaging.app"].search([])
            app_info = []
            for app in apps:
                if app.domain and not app.filtered_domain(safe_eval(app.domain)):
                    continue
                app_info.append(
                    {
                        "id": app.id,
                        "name": app.name,
                    }
                )
            study.app_info = app_info

    def do_app_action(self, app_id):
        self.ensure_one()
        app = self.env["medical.imaging.app"].browse(app_id).exists()
        if not app:
            return {}
        if app.app_type == "url":
            url = app.url
            if url and self.instance_uid:
                url = url.replace("{study_uid}", self.instance_uid)
                return {
                    "type": "ir.actions.act_url",
                    "url": url,
                    "target": "new",
                }
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
            "views": [[False, "form"]],
            "context": self.env.context,
        }
