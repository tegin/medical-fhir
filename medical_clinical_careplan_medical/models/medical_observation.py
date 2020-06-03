# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalObservation(models.Model):

    _inherit = "medical.observation"

    medical_message_id = fields.Many2one("medical.careplan.message")

    medical_careplan_medical_id = fields.Many2one("medical.careplan.medical")
