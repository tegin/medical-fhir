# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalEncounterCreateExternalRequest(models.TransientModel):

    _name = "medical.encounter.create.external.request"
    _description = "Generate report from encounter using a template"

    encounter_id = fields.Many2one(
        "medical.encounter",
        required=True,
        default=lambda r: r._default_encounter(),
    )
    patient_id = fields.Many2one(
        "medical.patient", default=lambda r: r._default_patient()
    )
    template_id = fields.Many2one(
        "medical.procedure.external.request.template", required=True
    )
    lang = fields.Selection(
        string="Language",
        selection="_get_lang",
        required=True,
        default=lambda r: r.env.user.lang,
    )

    @api.model
    def _default_encounter(self):
        if self.env.context.get("default_patient_id"):
            return (
                self.env["medical.patient"]
                .browse(self.env.context.get("default_patient_id"))
                ._get_last_encounter()
                .id
            )
        return self.env.context.get("default_encounter_id")

    @api.model
    def _default_patient(self):
        if self.env.context.get("default_encounter_id"):
            return (
                self.env["medical.encounter"]
                .browse(self.env.context.get("default_encounter_id"))
                .patient_id.id
            )
        return self.env.context.get("default_patient_id")

    @api.model
    def _get_lang(self):
        return self.env["res.lang"].get_installed()

    def _generate_kwargs(self):
        return {"encounter": self.encounter_id}

    def generate(self):
        self.ensure_one()
        report = self.template_id.with_context(
            lang=self.lang
        )._generate_request(**self._generate_kwargs())
        return report.with_context(
            form_view_initial_mode="edit"
        ).get_formview_action()
