# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalPatientCreateExternalRequest(models.TransientModel):

    _name = "medical.patient.create.external.request"
    _description = "Generate report from Patient using a template"

    encounter_id = fields.Many2one("medical.encounter", required=True)
    template_id = fields.Many2one(
        "medical.procedure.external.request.template", required=True
    )
    patient_id = fields.Many2one(
        related="encounter_id.patient_id",
        store=True,
        required=False,
        readonly=True,
    )
    lang = fields.Selection(
        string="Language",
        selection="_get_lang",
        required=True,
        default=lambda r: r.env.user.lang,
    )

    @api.model
    def _get_lang(self):
        return self.env["res.lang"].get_installed()

    def _generate_kwargs(self):
        return {"encounter": self.encounter_id}

    def generate(self):
        self.ensure_one()
        report = self.template_id.with_context(lang=self.lang)._generate_request(
            **self._generate_kwargs()
        )
        return report.get_formview_action()
