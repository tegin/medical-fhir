# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MedicalObservationTemplate(models.Model):

    _name = "medical.observation.template"
    _description = "Medical Observation Template"
    _rec_name = "name"

    name = fields.Char(required=True)
    concept_ids = fields.Many2many(
        "medical.observation.concept",
        string="Concepts",
    )
    group_ids = fields.Many2many(
        "res.groups",
    )
    user_id = fields.Many2one(
        "res.users",
        search="_search_user_id",
        store=False,
    )

    def _search_user_id(self, operator, value):
        if operator != "=":
            return []
        return [
            "|",
            ("group_ids", "=", False),
            ("group_ids", "in", self.env.user.groups_id.ids),
        ]
