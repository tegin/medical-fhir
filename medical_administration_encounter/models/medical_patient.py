# Copyright 2021 CreuBlanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MedicalPatient(models.Model):

    _inherit = "medical.patient"

    encounter_ids = fields.One2many(
        comodel_name="medical.encounter", inverse_name="patient_id"
    )
    encounter_count = fields.Integer(compute="_compute_encounter_count")

    @api.depends("encounter_ids")
    def _compute_encounter_count(self):
        for record in self:
            record.encounter_count = len(record.encounter_ids)

    def action_view_encounter_ids(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_administration_encounter.medical_encounter_action"
        )
        action["domain"] = [("patient_id", "=", self.id)]
        return action

    def _get_last_encounter(self):
        if not self.encounter_ids:
            raise ValidationError(_("No encounters can be found for this patient"))
        return self.encounter_ids[0]
