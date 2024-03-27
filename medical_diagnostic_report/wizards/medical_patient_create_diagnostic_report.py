# Copyright 2023 CreuBlanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class MedicalPatientCreateDiagnosticReport(models.TransientModel):

    _name = "medical.patient.create.diagnostic.report"
    _description = "Create a diagnostic report from patient"

    patient_id = fields.Many2one("medical.patient", requiered=True, readonly=True)
    template_id = fields.Many2one(
        "medical.diagnostic.report.template",
        required=True,
        domain="['|',('template_type','=','general'), '&', "
        "('create_uid','=',uid), ('template_type', '=', 'user')]",
    )
    lang = fields.Selection(
        string="Language",
        selection="_get_lang",
        required=True,
        default=lambda r: r.env.user.lang,
    )

    show_encounter_warning = fields.Boolean(default=False)
    encounter_warning = fields.Char(
        default="This encounter date is more than a week ago. Review it",
        readonly=True,
    )

    @api.model
    def _get_lang(self):
        return self.env["res.lang"].get_installed()

    def _generate_kwargs(self):
        return {"patient": self.patient_id}

    def generate(self):
        self.ensure_one()
        report = self.template_id.with_context(lang=self.lang)._generate_report(
            **self._generate_kwargs()
        )
        return report.get_formview_action()
