# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PatientPartnerSearch(models.TransientModel):

    _name = "patient.partner.search"

    partner_id = fields.Many2one("res.partner", name="Contact")
    patient_id = fields.Many2one("medical.patient", name="Patient")
    partner_type = fields.Selection(
        lambda self: self.env["medical.patient.partner"]
        ._fields["partner_type"]
        .selection,
        required=True,
    )

    def add_contact(self):
        for wizard in self:
            if wizard.partner_id and wizard.patient_id:
                patient_partner_obj = self.env["medical.patient.partner"]
                patient_partner_obj.create(
                    {
                        "partner_id": wizard.partner_id.id,
                        "patient_id": wizard.patient_id.id,
                        "partner_type": wizard.partner_type,
                    }
                )
        action = {"type": "ir.actions.act_window_close"}

        return action
