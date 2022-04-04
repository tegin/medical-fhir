# Copyright 2022 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MedicalProcedureExternalRequestTemplate(models.Model):
    _name = "medical.procedure.external.request.template"
    _description = "Procedure External Template"

    name = fields.Char(required=True)
    title = fields.Char(translate=True)
    composition = fields.Html(translate=True)
    active = fields.Boolean(default=True)

    def _generate_request_vals(self, encounter=None, **kwargs):
        return {
            "template_ids": [(4, self.id)],
            "encounter_id": encounter.id,
            "patient_name": encounter.patient_id.name,
            "vat": encounter.patient_id.vat,
            "patient_age": self._compute_age(encounter.patient_id),
            "composition": self.composition,
            "name": self.title or self.name,
            "lang": self.env.context.get("lang") or self.env.user.lang,
        }

    @api.model
    def _compute_age(self, patient):
        today = fields.Date.today()
        birth = patient.birth_date
        if not birth:
            return False
        age = (
            today.year
            - birth.year
            - ((today.month, today.day) < (birth.month, birth.day))
        )
        return age

    def _generate_request(self, **kwargs):
        return self.env["medical.procedure.external.request"].create(
            self._generate_request_vals(**kwargs)
        )
