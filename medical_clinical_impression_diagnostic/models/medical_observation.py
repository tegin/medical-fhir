# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalObservation(models.Model):
    _inherit = "medical.observation"

    clinical_impression_id = fields.Many2one(
        "medical.clinical.impression",
        ondelete="cascade",
        readonly=True,
    )

    def add_template(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "medical_clinical_impression_diagnostic.medical_observation_add_template_act_window"
        )
        action["context"] = self.env.context.copy()
        return action
