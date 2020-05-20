# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalCareplanMessage(models.Model):

    _name = "medical.careplan.message"
    _description = "Medical Careplan Message"
    _order = "message_date desc"

    medical_careplan_id = fields.Many2one(
        "medical.careplan.medical", required=True
    )

    message_text = fields.Html(required=True)
    message_date = fields.Datetime(required=True, default=fields.Datetime.now)

    user_creator = fields.Many2one(
        "res.users", required=True, default=lambda r: r.env.uid
    )
    partner_creator = fields.Many2one(
        "res.partner", related="create_uid.partner_id", store=True
    )

    medical_observation_ids = fields.One2many(
        "medical.observation", inverse_name="medical_message_id"
    )
